from __future__ import annotations

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from analysta import audit_dataframe


def test_audit_dataframe_flags_forbidden_nulls() -> None:
    df = pd.DataFrame({"id": [1, 2, 3], "value": [10, None, 30]})

    issues = audit_dataframe(df, allow_nulls={"value": False})

    assert not issues.empty
    null_issue = issues[issues["issue"] == "null_forbidden"].iloc[0]
    assert null_issue["column"] == "value"
    assert "Rows" in null_issue["details"]
    assert "1" in null_issue["details"]  # index of the null value


def test_audit_dataframe_detects_type_mismatches() -> None:
    df = pd.DataFrame(
        {
            "int_col": [1, 2.5, "3", "bad"],
            "float_col": [0.1, "0.2", "oops", 4],
        }
    )

    issues = audit_dataframe(
        df,
        expected_dtypes={"int_col": "int64", "float_col": "float64"},
    )

    assert {"int_col", "float_col"}.issubset(set(issues["column"]))

    int_issue = issues[issues["column"] == "int_col"].iloc[0]
    assert "2.5" in int_issue["details"]
    assert "bad" in int_issue["details"]

    float_issue = issues[issues["column"] == "float_col"].iloc[0]
    assert "oops" in float_issue["details"]


def test_audit_dataframe_validates_date_formats() -> None:
    df = pd.DataFrame(
        {
            "date": ["2024-01-01", "01/02/2024", "31-12-2023"],
        }
    )

    issues = audit_dataframe(df, date_formats={"date": ["%Y-%m-%d", "%m/%d/%Y"]})

    assert "invalid_date_format" in issues["issue"].values
    date_issue = issues[issues["issue"] == "invalid_date_format"].iloc[0]
    assert date_issue["column"] == "date"
    assert "31-12-2023" in date_issue["details"]


def test_audit_dataframe_infers_dtypes_for_unexpected_columns() -> None:
    df = pd.DataFrame(
        {
            "mostly_int": [1, 2, 3, "oops", 4.5],
        }
    )

    issues = audit_dataframe(df)

    assert "inferred_dtype_mismatch" in issues["issue"].values
    inferred_issue = issues[issues["issue"] == "inferred_dtype_mismatch"].iloc[0]
    assert inferred_issue["column"] == "mostly_int"
    assert "integer" in inferred_issue["details"]
    assert "oops" in inferred_issue["details"]


def test_audit_dataframe_inferred_dtype_can_be_disabled() -> None:
    df = pd.DataFrame(
        {
            "mostly_int": [1, 2, 3, "oops", 4.5],
        }
    )

    issues = audit_dataframe(df, infer_dtypes=False)

    assert issues.empty
