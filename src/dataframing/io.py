"""
    dataframing.io
    ~~~~~~~~~~~~~~

    Input and output method for dataframes, including hashing methods.

    :copyright: (c) 2023 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

import hashlib
import pathlib
from typing import Any, Callable, Literal

import pandas as pd

MISSING = object()

KEY_HASH = "HASH"


def hash_dataframe(df: pd.DataFrame) -> str:
    """Return a data hash of the Index/Series/DataFrame."""
    if KEY_HASH in df.attrs:
        stored_hash = df.attrs[KEY_HASH]
        df.attrs[KEY_HASH] = "0"
    new_hash = hashlib.sha256(
        pd.util.hash_pandas_object(df, index=True).values
    ).hexdigest()
    if KEY_HASH in df.attrs:
        df.attrs[KEY_HASH] = stored_hash
    return new_hash


def _check_valid_extensions(filename: str | pathlib.Path | pd.ExcelFile):
    """Check if the file extension is supported.

    Raises
    ------
    ValueError
        If the extension is not supported.

    """
    if isinstance(filename, str) and not filename.endswith(".xlsx"):
        raise ValueError("Only excel files (.xlsx) are currently supported.")
    elif isinstance(filename, pathlib.Path) and filename.suffix == ".xlsx":
        raise ValueError("Only excel files (.xlsx) are currently supported.")


def load(
    filename: str | pathlib.Path | pd.ExcelFile,
    sheet_name: str = "Sheet1",
    *,
    use_hash: bool = True,
    converters: dict[str, Callable[[str, Any], Any]] | None = None,
) -> pd.DataFrame:
    """Load a dataframe from a file, including metadata.

    Metadata should be stored in sheet named '_attrs_{sheet_name}'
    and will be returned in the `.attrs` mapping

    *HASH* metadata will not be returned within attrs.

    Parameters
    ----------
    filename
        Input file or filepath.
    sheet_name, optional
        Name of the sheet to load, by default "Sheet1"
    use_hash, optional
        If True (default), the hash will be loaded from the
        metadata and compared to the actual content.

    Returns
    -------
        The resulting dataframe.
    """

    if not isinstance(filename, pd.ExcelFile):
        _check_valid_extensions(filename)

    df = pd.read_excel(filename, sheet_name=sheet_name, converters=converters)
    metadata = pd.read_excel(filename, sheet_name="_attrs_" + sheet_name)

    stored_hash = None

    for _, row in metadata.iterrows():
        df.attrs[row.key] = row.value
        if row.key == KEY_HASH:
            stored_hash = row.value

    if use_hash:
        if stored_hash is None:
            raise ValueError("DataFrame hash not stored in file, cannot verify.")
        calculated_hash = hash_dataframe(df)
        if calculated_hash != stored_hash:
            raise ValueError(
                f"Stored DataFrame does not match content\n"
                f"{stored_hash} vs. {calculated_hash}"
            )

    return df


def load_many(
    filename: str | pathlib.Path,
    *,
    use_hash: bool = True,
    converters: dict[str, dict[str, Callable[[str, Any], Any]]] | None = None,
) -> dict[str, pd.DataFrame]:
    """Load all sheet within a file into dictionary.

    See also `load`.

    Parameters
    ----------
    filename
        Input file or filepath.
    use_hash, optional
        If True (default), the hash will be loaded from the
        metadata and compared to the actual content.

    Returns
    -------
        A sheet name to DataFrame Mapping.
    """
    _check_valid_extensions(filename)

    with pd.ExcelFile(filename) as xls:
        return {
            sheet_name: load(
                xls,
                sheet_name,
                use_hash=use_hash,
                converters=converters.get(sheet_name, None),
            )
            for sheet_name in xls.sheet_names
            if not sheet_name.startswith("_attrs_")
        }


def save(
    df: pd.DataFrame,
    filename: str | pathlib.Path | pd.ExcelWriter,
    sheet_name: str = "Sheet1",
    *,
    use_hash: bool = True,
):
    """Save dataframe to file.

    Metadata will be stored in sheet named '_attrs_{sheet_name}'
    and obtained from `.attrs` mapping

    Parameters
    ----------
    df
        Dataframe to be saved.
    filename
        Output file or filepath.
    sheet_name, optional
        Name of the sheet to save, by default "Sheet1"
    use_hash, optional
        If True (default), the hash will be loaded from the
        metadata and compared to the actual content.
    """

    if not isinstance(filename, pd.ExcelWriter):
        _check_valid_extensions(filename)

    metadata = [dict(key=k, value=v) for k, v in df.attrs.items()]

    if use_hash:
        df.attrs[KEY_HASH] = "0"
        metadata.append(dict(key=KEY_HASH, value=hash_dataframe(df)))
    metadata = pd.DataFrame(metadata)

    if isinstance(filename, pd.ExcelWriter):
        writer = filename
    else:
        writer = pd.ExcelWriter(filename)

    try:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        metadata.to_excel(writer, sheet_name="_attrs_" + sheet_name, index=False)
    finally:
        if not isinstance(filename, pd.ExcelWriter):
            writer.close()


def save_many(
    dfs: dict[str, pd.DataFrame],
    filename: str | pathlib.Path,
    *,
    use_hash: bool = True,
    mode: Literal["w", "a"] = "a",
    if_sheet_exists: Literal["error", "new", "replace", "overlay"] = "replace",
):
    """Save multiple dataframes to a file.

    Parameters
    ----------
    dfs
        A sheet name to DataFrame Mapping.
    filename
        Output file or filepath.
    sheet_name, optional
        Name of the sheet to save, by default "Sheet1"
    use_hash, optional
        If True (default), the hash will be loaded from the
        metadata and compared to the actual content.
    """

    _check_valid_extensions(filename)

    if mode == "a":
        with pd.ExcelWriter(
            filename, mode=mode, if_sheet_exists=if_sheet_exists
        ) as writer:
            for sheet_name, df in dfs.items():
                save(df, writer, sheet_name, use_hash=use_hash)
    elif mode == "w":
        with pd.ExcelWriter(filename, mode=mode) as writer:
            for sheet_name, df in dfs.items():
                save(df, writer, sheet_name, use_hash=use_hash)
