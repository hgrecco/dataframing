"""
    dataframing.protocols
    ~~~~~~~~~~~~~~~~~~~~~

    Protocols used within the pacakge.

    :copyright: (c) 2023 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""


from typing import Any, Protocol


class SupportsGetItem(Protocol):
    def __getitem__(self, key: str) -> Any:
        ...


class SupportsSetItem(Protocol):
    def __setitem__(self, key: str, object: Any):
        ...


class SupportsGetSetItem(SupportsGetItem, SupportsSetItem, Protocol):
    ...
