from typing import Any, Callable, Generator, Literal, Protocol, Self, TypedDict, TypeVar

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

    def query(self, expr: str, *, inplace: bool = True, **kwargs: Any) -> Self:
        ...

    def iterrows(self) -> Generator[tuple[Any, T], None, None]:
        ...

    def sort_values(
        self,
        by: str | list[str],
        *,
        axis: Literal[0, 1, "index", "columns"] = 0,
        ascending: bool = True,
        inplace: bool = False,
        kind: Literal["quicksort", "mergesort", "heapsort", "stable"] = "quicksort",
        na_position: Literal["first", "last"] = "last",
        ignore_index: bool = False,
        key: Callable[..., Any] | None = None,
    ) -> Self:
        ...

    def replace(
        self,
        to_replace: Any = None,
        value: Any = None,
        *,
        inplace: bool = False,
        regex: Any = False,
    ) -> Self:
        ...
