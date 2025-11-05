"""Convenient CSV and Excel helpers built on top of pandas."""

from __future__ import annotations

import os
from typing import IO, Any, BinaryIO, TextIO

import pandas as pd
from pandas import DataFrame

FilePath = str | os.PathLike[str]
ReadCsvBuffer = TextIO | BinaryIO
WriteCsvBuffer = TextIO | BinaryIO
ReadExcelBuffer = IO[bytes]
WriteExcelBuffer = IO[bytes]


def read_csv(
    path_or_buffer: FilePath | ReadCsvBuffer,
    /,
    **kwargs: Any,
) -> DataFrame:
    """Return a DataFrame by delegating to :func:`pandas.read_csv`.

    Parameters
    ----------
    path_or_buffer:
        A file path string, pathlib.Path, or file-like object to read the CSV
        data from.
    **kwargs:
        Additional keyword arguments passed directly to
        :func:`pandas.read_csv` (e.g. ``dtype`` or ``parse_dates``).
    """

    return pd.read_csv(path_or_buffer, **kwargs)


def write_csv(
    dataframe: DataFrame,
    path_or_buffer: FilePath | WriteCsvBuffer,
    /,
    *,
    index: bool | None = None,
    **kwargs: Any,
) -> None:
    """Write a DataFrame to CSV using :meth:`pandas.DataFrame.to_csv`.

    Parameters
    ----------
    dataframe:
        The DataFrame to be written to disk or a buffer.
    path_or_buffer:
        A file path string, pathlib.Path, or file-like object to write the CSV
        into.
    index:
        Whether to include the DataFrame index in the output. ``None`` keeps
        pandas' default behaviour (``True``).
    **kwargs:
        Additional keyword arguments forwarded to
        :meth:`pandas.DataFrame.to_csv` (e.g. ``sep`` or ``encoding``).
    """

    to_csv_kwargs: dict[str, Any] = {}
    if index is not None:
        to_csv_kwargs["index"] = index
    dataframe.to_csv(path_or_buffer, **to_csv_kwargs, **kwargs)


def read_excel(
    path_or_buffer: FilePath | ReadExcelBuffer,
    /,
    **kwargs: Any,
) -> DataFrame:
    """Return a DataFrame by delegating to :func:`pandas.read_excel`.

    Parameters
    ----------
    path_or_buffer:
        A file path string, pathlib.Path, or file-like object containing Excel
        data.
    **kwargs:
        Additional keyword arguments passed directly to
        :func:`pandas.read_excel` (e.g. ``sheet_name`` or ``engine``).
    """

    return pd.read_excel(path_or_buffer, **kwargs)


def write_excel(
    dataframe: DataFrame,
    path_or_buffer: FilePath | WriteExcelBuffer,
    /,
    *,
    sheet_name: str | None = None,
    index: bool | None = None,
    **kwargs: Any,
) -> None:
    """Write a DataFrame to Excel via :meth:`pandas.DataFrame.to_excel`.

    Parameters
    ----------
    dataframe:
        The DataFrame to be written to the Excel workbook.
    path_or_buffer:
        Destination path or Excel-compatible buffer.
    sheet_name:
        Optional sheet name for the exported data. ``None`` keeps pandas'
        default (``"Sheet1"``).
    index:
        Whether to include the DataFrame index in the output. ``None`` keeps
        pandas' default behaviour (``True``).
    **kwargs:
        Additional keyword arguments forwarded to
        :meth:`pandas.DataFrame.to_excel` (e.g. ``engine``).
    """

    to_excel_kwargs: dict[str, Any] = {}
    if sheet_name is not None:
        to_excel_kwargs["sheet_name"] = sheet_name
    if index is not None:
        to_excel_kwargs["index"] = index

    dataframe.to_excel(path_or_buffer, **to_excel_kwargs, **kwargs)
