"""Utility helpers for :mod:`analysta`."""

from __future__ import annotations

import pandas as pd


def hello() -> None:
    """Print a friendly greeting."""

    print("Hello, Analysta!")


def trim_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Return *df* with leading/trailing whitespace stripped from strings."""

    trimmed = df.copy()

    for column in trimmed.columns:
        series = trimmed[column]
        if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
            trimmed[column] = series.apply(
                lambda value: value.strip() if isinstance(value, str) else value
            )

    return trimmed


def find_duplicates(
    df: pd.DataFrame,
    column: str | list[str] | None = None,
    *,
    counts: bool = False,
) -> pd.DataFrame:
    """Return duplicate rows or their counts.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to check for duplicates.
    column : str | list[str] | None, optional
        Column(s) to consider when looking for duplicates. If ``None`` (default),
        all columns are used.
    counts : bool, default ``False``
        When ``True``, return a DataFrame with duplicate values and how many
        times they appear instead of the duplicated rows themselves.

    Returns
    -------
    pandas.DataFrame
        Either the duplicated rows or a count of duplicates by the selected
        column(s).
    """

    if column is None:
        subset = df.columns.tolist()
    elif isinstance(column, str):
        subset = [column]
    else:
        subset = list(column)
    mask = df.duplicated(subset=subset, keep=False)
    dupes = df.loc[mask].copy()

    if counts:
        return dupes.groupby(subset).size().reset_index(name="count")

    return dupes.reset_index(drop=True)


def duplicates(
    df: pd.DataFrame,
    column: str | None = None,
    *,
    counts: bool = False,
) -> pd.DataFrame:
    """Convenience alias for :func:`find_duplicates`.

    This shorter name keeps examples concise while preserving
    ``find_duplicates`` for backward compatibility.
    """

    return find_duplicates(df, column=column, counts=counts)
