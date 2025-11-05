"""Utilities for auditing DataFrame quality issues."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_numeric_dtype,
    is_string_dtype,
    pandas_dtype,
)

Issue = dict[str, str]


def audit_dataframe(
    df: pd.DataFrame,
    *,
    allow_nulls: Mapping[str, bool] | None = None,
    expected_dtypes: Mapping[str, Any] | None = None,
    date_formats: Mapping[str, str | Sequence[str]] | None = None,
    infer_dtypes: bool = True,
) -> pd.DataFrame:
    """Inspect *df* for basic data quality issues.

    Parameters
    ----------
    df:
        The DataFrame to validate.
    allow_nulls:
        Mapping of column name to ``True``/``False`` indicating whether nulls are
        allowed for the column. Columns omitted from the mapping are not
        validated.
    expected_dtypes:
        Mapping of column name to an expected dtype (``numpy``/``pandas`` dtype,
        dtype string, or Python type).
    date_formats:
        Mapping of column name to the ``strftime`` format string (or sequence of
        strings) that should successfully parse values in the column.
    infer_dtypes:
        If ``True`` (the default), inspect columns not listed in ``expected_dtypes``
        to infer their predominant dtype and surface values that do not match the
        inferred category.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns ``column``, ``issue`` and ``details``.
    """

    issues: list[Issue] = []
    allow_nulls = allow_nulls or {}
    expected_dtypes = expected_dtypes or {}
    date_formats = date_formats or {}

    for column, allow in allow_nulls.items():
        if allow:
            continue
        if column not in df.columns:
            continue
        series = df[column]
        null_mask = series.isna()
        if null_mask.any():
            indices = list(series.index[null_mask])
            issues.append(
                {
                    "column": column,
                    "issue": "null_forbidden",
                    "details": _summarise_values("null", indices),
                }
            )

    for column, expected in expected_dtypes.items():
        if column not in df.columns:
            continue
        series = df[column]
        non_null_series = series[~series.isna()]
        if non_null_series.empty:
            continue
        mismatch_mask = _type_mismatch_mask(non_null_series, expected)
        if mismatch_mask is None:
            continue
        if mismatch_mask.any():
            invalid = non_null_series[mismatch_mask]
            issues.append(
                {
                    "column": column,
                    "issue": "dtype_mismatch",
                    "details": _summarise_invalid_values(expected, invalid),
                }
            )

    for column, formats in date_formats.items():
        if column not in df.columns:
            continue
        series = df[column]
        non_null_series = series[~series.isna()]
        if non_null_series.empty:
            continue
        if is_datetime64_any_dtype(non_null_series):
            continue
        invalid_mask = _date_invalid_mask(non_null_series, formats)
        if invalid_mask.any():
            invalid = non_null_series[invalid_mask]
            issues.append(
                {
                    "column": column,
                    "issue": "invalid_date_format",
                    "details": _summarise_values(invalid, list(invalid.index)),
                }
            )

    if infer_dtypes:
        for column in df.columns:
            if column in expected_dtypes:
                continue
            series = df[column]
            non_null_series = series[~series.isna()]
            if non_null_series.empty:
                continue
            inferred_category = _infer_predominant_category(non_null_series)
            if inferred_category is None:
                continue
            mismatch_mask = non_null_series.map(
                lambda value: _categorise_value(value) != inferred_category
            )
            if mismatch_mask.any():
                invalid = non_null_series[mismatch_mask]
                issues.append(
                    {
                        "column": column,
                        "issue": "inferred_dtype_mismatch",
                        "details": _summarise_invalid_values(
                            inferred_category, invalid
                        ),
                    }
                )

    if issues:
        result = pd.DataFrame(issues, columns=["column", "issue", "details"])
        return result.sort_values(["column", "issue"], ignore_index=True)
    return pd.DataFrame(columns=["column", "issue", "details"])


def _type_mismatch_mask(series: pd.Series, expected: Any) -> pd.Series | None:
    category = _normalise_dtype(expected)
    if category == "integer":
        converted = pd.to_numeric(series, errors="coerce")
        fractional = converted % 1
        fractional_mask = pd.Series(
            ~np.isclose(fractional.fillna(0), 0), index=converted.index
        )
        fractional_mask &= converted.notna()
        invalid = series.notna() & (converted.isna() | fractional_mask)
        return invalid
    if category == "float":
        converted = pd.to_numeric(series, errors="coerce")
        invalid = series.notna() & converted.isna()
        return invalid
    if category == "string":
        invalid = series.notna() & ~series.map(lambda value: isinstance(value, str))
        return invalid
    if category == "datetime":
        parsed = pd.to_datetime(series, errors="coerce")
        invalid = series.notna() & parsed.isna()
        return invalid
    return None


def _normalise_dtype(expected: Any) -> str:
    try:
        dtype = pandas_dtype(expected)
    except (TypeError, ValueError):
        dtype = None

    if dtype is not None:
        if is_integer_dtype(dtype):
            return "integer"
        if is_float_dtype(dtype) or (is_numeric_dtype(dtype) and not is_integer_dtype(dtype)):
            return "float"
        if is_string_dtype(dtype):
            return "string"
        if is_datetime64_any_dtype(dtype):
            return "datetime"

    if isinstance(expected, type):
        if issubclass(expected, (int, np.integer)):
            return "integer"
        if issubclass(expected, (float, np.floating)):
            return "float"
        if issubclass(expected, (str, bytes)):
            return "string"

    if isinstance(expected, str):
        lower = expected.lower()
        if "int" in lower:
            return "integer"
        if any(token in lower for token in ("float", "double", "numeric", "number")):
            return "float"
        if "datetime" in lower or lower.startswith("date"):
            return "datetime"
        if lower in {"str", "string", "object"}:
            return "string"

    return "unknown"


def _date_invalid_mask(series: pd.Series, formats: str | Sequence[str]) -> pd.Series:
    if isinstance(formats, str):
        formats_to_try: list[str] = [formats]
    elif isinstance(formats, Sequence) and not isinstance(formats, (bytes, bytearray)):
        formats_to_try = [str(fmt) for fmt in formats]
    else:
        formats_to_try = [str(formats)]

    valid_mask = pd.Series(False, index=series.index)
    for fmt in formats_to_try:
        parsed = pd.to_datetime(series, format=fmt, errors="coerce")
        valid_mask |= parsed.notna()
    return ~valid_mask


def _summarise_values(values: Any, indices: list[Any]) -> str:
    if isinstance(values, pd.Series):
        sample = values.astype(str).head(5).tolist()
    elif hasattr(values, "__iter__") and not isinstance(values, (str, bytes)):
        sample = list(map(str, list(values)[:5]))
    else:
        sample = [str(values)]
    return f"Rows {indices}; samples: {sample}"


def _summarise_invalid_values(expected: Any, invalid: pd.Series) -> str:
    sample_values = invalid.astype(str).head(5).tolist()
    indices = list(invalid.index)
    return f"Expected {expected!r}; rows {indices}; samples: {sample_values}"


def _infer_predominant_category(series: pd.Series) -> str | None:
    categories = series.map(_categorise_value).dropna()
    if categories.empty:
        return None
    counts = categories.value_counts()
    if counts.empty:
        return None
    return counts.idxmax()


def _categorise_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (pd.Timestamp, np.datetime64, datetime)):
        return "datetime"
    if isinstance(value, (bool, np.bool_)):
        return "boolean"
    if isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_)):
        return "integer"
    if isinstance(value, (float, np.floating)):
        return "float"
    if isinstance(value, str):
        return "string"
    return type(value).__name__
