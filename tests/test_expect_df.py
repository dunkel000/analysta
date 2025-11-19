import pandas as pd

from analysta.check import expect_df


def test_unique_constraint_catches_duplicates():
    df = pd.DataFrame({"id": [1, 1, 2]})

    report = expect_df(df, "column id should be unique")

    assert report.passed is False
    assert report.column_results[0].passed is False
    assert "duplicate" in report.column_results[0].diagnostics[0]


def test_dtype_and_format_constraints_report_details():
    df = pd.DataFrame(
        {
            "age": [25, "oops"],
            "created": ["2024-01-01", "2024-13-01"],
        }
    )

    expectations = [
        "column age: integer",
        "column created should be datetime format %Y-%m-%d",
    ]

    report = expect_df(df, expectations)

    age_result = next(result for result in report.column_results if result.column == "age")
    assert age_result.passed is False
    assert "expected integer" in age_result.diagnostics[0]

    created_result = next(result for result in report.column_results if result.column == "created")
    assert created_result.passed is False
    assert "format=%Y-%m-%d" in created_result.diagnostics[0]


def test_allowed_values_constraint_reports_invalid_entries():
    df = pd.DataFrame({"status": ["ok", "bad", "pending"]})

    report = expect_df(df, "column status: allowed values {ok, pending}")

    status_result = report.column_results[0]
    assert status_result.passed is False
    assert "unexpected values" in status_result.diagnostics[0]


def test_regex_constraint_flags_non_matching_rows():
    df = pd.DataFrame({"code": ["AB12", "XX99", "invalid"]})

    report = expect_df(df, "column code should match regex ^[A-Z]{2}\\d{2}$")

    code_result = report.column_results[0]
    assert code_result.passed is False
    assert "regex mismatch" in code_result.diagnostics[0]


def test_nullability_constraint_detects_null_rows():
    df = pd.DataFrame({"name": ["a", None]})

    report = expect_df(df, "column name must be not null")

    name_result = report.column_results[0]
    assert name_result.passed is False
    assert "nulls forbidden" in name_result.diagnostics[0]


def test_row_rule_evaluation_uses_expression_results():
    df = pd.DataFrame({"amount": [10, -5, 0]})

    report = expect_df(df, "column amount: float", row_rules=["rows must satisfy amount >= 0"])

    assert report.row_results[0].passed is False
    assert report.row_results[0].failing_indices == [1]
    assert "amount >= 0" in report.row_results[0].message


def test_custom_validators_support_series_and_messages():
    df = pd.DataFrame({"score": [5, -1, 10]})

    def non_negative(series_df: pd.DataFrame):
        return series_df["score"] >= 0

    def min_threshold(series_df: pd.DataFrame):
        mask = series_df["score"] >= 2
        return mask, "scores must be at least 2"

    report = expect_df(
        df,
        "column score: integer",
        validators=[("non-negative score", non_negative), ("min threshold", min_threshold)],
    )

    assert report.custom_results[0].description == "non-negative score"
    assert report.custom_results[0].failing_indices == [1]

    assert report.custom_results[1].description == "min threshold"
    assert report.custom_results[1].failing_indices == [1]
    assert report.custom_results[1].message == "scores must be at least 2"


def test_expect_df_integration_matches_human_readable_report():
    df = pd.DataFrame(
        {
            "id": [1, 1, 2],
            "placed_at": ["2024-01-01", "2024-13-01", "2024-01-03"],
            "status": ["ok", "pending", None],
            "amount": [10.0, -5.0, 5.0],
        }
    )

    expectations = [
        "expect column id to be unique and not null",
        "column placed_at: datetime format %Y-%m-%d",
        "column status: allowed values {ok, pending}; allow nulls",
        "column amount: float",
    ]

    def amount_not_zero(frame: pd.DataFrame):
        return (frame["amount"] != 0) | frame["amount"].isna()

    report = expect_df(
        df,
        expectations,
        row_rules=["rows must satisfy amount >= 0"],
        validators=[("amount not zero", amount_not_zero)],
    )

    assert report.passed is False
    assert len(report.column_results) == 4
    assert len(report.row_results) == 1
    assert len(report.custom_results) == 1

    expected_report = """
Expectation report: FAILED
Columns:
- id: FAIL -> expected unique values; duplicate rows [0, 1]; samples: [1, 1]
- placed_at: FAIL -> expected datetime; rows [1]; samples: ['2024-13-01']; format=%Y-%m-%d
- status: PASS
- amount: PASS
Row rules:
- rows must satisfy amount >= 0: FAIL -> rows failing rule 'amount >= 0': [1]
Custom validators:
- amount not zero: PASS
""".strip()

    assert report.to_human_readable() == expected_report
