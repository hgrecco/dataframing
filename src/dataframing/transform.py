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
    source_typed_dict = get_type_hints(func_types["source"])
    target_typed_dict = get_type_hints(func_types["target"])
    intersect_keys = set(source_typed_dict).intersection(set(target_typed_dict))

    def _inner(source: S) -> T:
        token = var_intersect_keys.set(intersect_keys)
        target = {}  # type: ignore
        func(source, target)
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
