"""
    dataframing.transform
    ~~~~~~~~~~~~~~~~~~~~~

    Classes and functions for dataframe transformations.

    :copyright: (c) 2023 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""


import contextlib
import dis
import inspect
from collections.abc import Collection
from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    ParamSpec,
    Protocol,
    TypeVar,
    overload,
)

from pandas import DataFrame

from .protocols import SupportsGetItem

S = TypeVar("S")
T = TypeVar("T")

P = ParamSpec("P")
R = TypeVar("R")


def expecting(offset: int = 0) -> int:
    """Return how many values the caller is expecting"""
    f = inspect.currentframe().f_back.f_back
    i = f.f_lasti + offset
    bytecode = f.f_code.co_code
    instruction = bytecode[i]
    if instruction == dis.opmap["UNPACK_SEQUENCE"]:
        return bytecode[i + 1]
    elif instruction == dis.opmap["POP_TOP"]:
        return 0
    else:
        return 1


class AttrGetter:
    """Given a protocol, will return the name of the attribute
    if the attribute is present within the protocol.

    Raises
    ------
    ValueError
        If the attribute is not present within the protocol.
    """

    def __init__(self, protocol: Protocol) -> None:
        self._protocol = protocol

    def __getattr__(self, name: str) -> str:
        if name not in self._protocol.__annotations__:
            raise ValueError(f"{self._protocol} does not have a {name} attribute.")
        return name


class AttrSetter:
    """Given a protocol, will enable to set an attribute
    if the attribute is present within the protocol.

    Raises
    ------
    ValueError
        If the attribute is not present within the protocol.
    """

    def __init__(self, protocol: Protocol) -> None:
        self._protocol = protocol
        self._content: dict[str, Any] = {}

    def __setattr__(self, name: str, value: Any):
        if name == "_content" or name == "_protocol":
            return super().__setattr__(name, value)
        if name not in self._protocol.__annotations__:
            raise ValueError(f"{self._protocol} does not have a {name} attribute.")
        self._content[name] = value

    def __iter__(self):
        return iter(self._content.items())


class Mapper:
    """Helper class to map a record into another record."""

    def __init__(
        self,
        func: Callable[
            [
                SupportsGetItem,
            ],
            Any,
        ],
    ) -> None:
        self.func = func
        self._ready = False

    def __call__(self, record: SupportsGetItem) -> Any:
        out = self.func(record)
        self._ready = True
        return out

    def __getattr__(self, name: str) -> Any:
        return FutureGetAttr(self, name)

    def __getitem__(self, item: Any) -> Any:
        return FutureGetItem(self, item)

    def __iter__(self):
        for n in range(expecting(offset=0)):
            yield self[n]


class FutureGetItem:
    """Helper class to extract an item after the mapper has been executed."""

    def __init__(self, mapper: Mapper, item: Any) -> None:
        self.mapper = mapper
        self.item = item


class FutureGetAttr:
    """Helper class to extract an attribute after the mapper has been executed."""

    def __init__(self, mapper: Mapper, item: str) -> None:
        self.mapper = mapper
        self.item = item


def use(func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    """Creates a callable that can be used with records.

    Given a callable and protocol attributes given as args and kwargs,
    creates a new callable that will accept a record.

    This new callable will extract the protocol attributes from the record
    and used them as args and kwargs for the original callable.
    """

    def _from_dict(record: SupportsGetItem) -> R:
        return func(
            *(record[k] for k in args), **{k: record[v] for k, v in kwargs.items()}
        )  # type: ignore

    return Mapper(_from_dict)


class Transformer(Generic[S, T]):
    """A transformer object allows to generate a set of rules
    to transform a record into another and then use them.

    Example
    -------
    >>> class Def1(Protocol):
    ...     last_name: str
    ...     first_name: str
    >>> class Def2(Protocol):
    ...    full_name: str
    >>> with Transformer.build(Def1, Def2) as (transformer, source, target):
    ...    target.full_name = use("{}, {}".format, source.last_name, source.first_name)
    >>> record = dict(last_name="Grecco", first_name="Hernán")
    >>> transformer.transform_record(record)

    """

    def __init__(self, source: AttrGetter, target: AttrSetter):
        self.source = source
        self.target = target

    def transform_record(
        self, record: dict[str, Any], out: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Transform a record.

        Use `out` to provide a location into which the result is stored.
        """
        cache = {}
        if out is None:
            out = record

        for target_key, source in self.target:
            if isinstance(source, FutureGetItem):
                if source.mapper not in cache:
                    cache[source.mapper] = source.mapper(record)

                out[target_key] = cache[source.mapper][source.item]
            elif isinstance(source, FutureGetAttr):
                if source.mapper not in cache:
                    cache[source.mapper] = source.mapper(record)

                out[target_key] = getattr(cache[source.mapper], source.item)
            elif isinstance(source, Mapper):
                out[target_key] = source(record)
            else:
                out[target_key] = source

        return out

    def transform_collection(self, source: Collection[S]) -> Collection[T]:
        """Transform a collection of records."""
        if isinstance(source, DataFrame):
            return DataFrame(self.transform_collection(source.to_dict("records")))

        out = []
        for el in source:
            out_el = el.__class__()
            out.append(self.transform_record(el, out_el))

        return source.__class__(out)

    @overload
    def __call__(self, source: S) -> T:
        ...

    @overload
    def __call__(self, source: Collection[S]) -> Collection[T]:
        ...

    def __call__(self, source):
        if isinstance(source, dict):
            return self.transform_record(source)
        return self.transform_collection(source)

    @contextlib.contextmanager
    @staticmethod
    def build(
        source: type[S], target: type[T]
    ) -> Generator[tuple["Transformer[S, T]", S, T], None, None]:
        """Build a transformer class

        Parameters
        ----------
        source
            A protocol describing the source record.
        target
            A protocol describing the target record.

        Yields
        ------
            The resulting transformer.
            A proxy for a source record.
            A proxy for a target record.
        """
        source = AttrGetter(source)  # type: ignore
        target = AttrSetter(target)  # type: ignore
        yield Transformer(source, target), source, target  # type: ignore
