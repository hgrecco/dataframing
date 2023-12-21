"""
    dataframing.transform
    ~~~~~~~~~~~~~~~~~~~~~

    Classes and functions for dataframe transformations.

    :copyright: (c) 2023 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

import copy as _copy
from contextvars import ContextVar
from typing import (
    Callable,
    Generic,
    TypedDict,
    TypeVar,
    _TypedDictMeta,
    get_type_hints,
)

import pandas as pd

try:
    from mpire import WorkerPool  # type: ignore
except ImportError:

    def WorkerPool(*args, **kwargs):  # type: ignore
        raise ValueError(
            "Using more than one process to calculate require mpire.\n"
            "pip install mpire"
        )


S = TypeVar("S", bound=TypedDict)
T = TypeVar("T", bound=TypedDict)

var_intersect_keys = ContextVar("var")


def copy(source: S, target: T) -> None:
    intersect_keys = var_intersect_keys.get()
    for name in intersect_keys:
        target[name] = _copy.deepcopy(source[name])


class Transformer(Generic[S, T]):
    @staticmethod
    def __call__(source: S) -> T:
        ...

    @staticmethod
    def map(records: pd.DataFrame, *, max_workers: int | None = 1) -> pd.DataFrame:
        ...


def wrap(func: Callable[[S, T], None]) -> Transformer[S, T]:
    func_types = get_type_hints(func)
    args = list(func_types.keys())
    source_type = func_types[args[0]]
    target_type = func_types[args[1]]
    if not isinstance(source_type, _TypedDictMeta):
        raise TypeError(
            f"The first parameter ({args[0]}) annotation must be "
            f"a subclass TypeDict, not {source_type}"
        )
    if not isinstance(target_type, _TypedDictMeta):
        raise TypeError(
            f"The second parameter ({args[1]}) annotation must be "
            f"a subclass TypeDict, not {source_type}"
        )
    if "return" in args and func_types["return"] is not type(None):
        rtype = func_types["return"]
        raise TypeError(f"The return type must be None, not {rtype}")
    count_args = len(args) - +(1 if "return" in args else 0)
    if count_args != 2:
        raise ValueError(
            f"The function must have exactly two arguments, " f"not {count_args}"
        )

    source_typed_dict = get_type_hints(source_type)
    target_typed_dict = get_type_hints(target_type)
    intersect_keys = set(source_typed_dict).intersection(set(target_typed_dict))

    def _inner(source: S) -> T:
        token = var_intersect_keys.set(intersect_keys)
        target = {}  # type: ignore

        try:
            func(source, target)
        except Exception as ex:
            if "exception" in target_typed_dict:
                target["exception"] = str(ex)
            else:
                ex.add_note(repr(source))
                raise ex

        var_intersect_keys.reset(token)
        return target

    def _map(records: pd.DataFrame, *, max_workers: int | None = 1) -> pd.DataFrame:
        if max_workers == 1:
            out_records = records.apply(_inner, axis=1)
        else:
            records = list((record,) for record in records.to_dict("records"))
            with WorkerPool(n_jobs=max_workers) as pool:
                out_records = pool.map(_inner, records)

        return pd.DataFrame(list(out_records))

    _inner.map = _map

    return _inner
