from typing import Any, Generator, Protocol, Self, TypedDict, TypeVar

T = TypeVar("T", bound=TypedDict, covariant=True)


class Accesor(Protocol[T]):
    def __getitem__(self, __key: Any) -> T:
        ...


class DataFrameLike(Protocol[T]):
    @property
    def at(self) -> Accesor[T]:
        ...

    @property
    def iat(self) -> Accesor[T]:
        ...

    @property
    def loc(self) -> Accesor[T]:
        ...

    @property
    def iloc(self) -> Accesor[T]:
        ...

    def query(self, expr: str, *, inplace: bool, **kwargs: Any) -> Self:
        ...

    def iterrows(self) -> Generator[tuple[Any, T], None, None]:
        ...
