from typing import Any, Callable, TypedDict, get_type_hints

from typeguard import check_type

from .dflike import DataFrameLike


def safe_int(value: Any) -> int:
    if value is None:
        return 0
    elif isinstance(value, str):
        return int(value.strip() or 0)
    elif isinstance(value, float):
        val = int(value)
        if val != value:
            raise ValueError("While converting float to int, value changed.")
        return val
    elif isinstance(value, int):
        return value

    val = int(value)
    if val != value:
        raise ValueError(f"While converting {type(value)} to int, value changed.")
    return val


def NoneTo(
    default: Any
) -> Callable[
    [
        Any,
    ],
    Any,
]:
    def _inner(value: Any) -> Any:
        if value is None:
            return default
        return value

    return _inner


def validate[T: TypedDict](records: DataFrameLike[T], schema: type[T]) -> bool:
    is_ok = True
    for ndx, (_, record) in enumerate(records.iterrows()):
        for column_name, column_type in get_type_hints(schema).items():
            value = record[column_name]
            try:
                check_type(value, column_type)
            except Exception:
                is_ok = False
                print(
                    f"In row {ndx} and column {column_name}, "
                    f"expected {column_type} found {type(value)}: {value}"
                )

    return is_ok
