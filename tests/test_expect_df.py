import pandas as pd

from analysta.check import expect_df


def test_expect_df_parses_natural_language_expectations():
    df = pd.DataFrame(
        {
            "id": [1, 1, 2],
            "age": [25, "x", None],
            "status": ["active", "inactive", "pending"],
        }
    )

    expectations = """
    expect column id to be unique and not null
    column age: integer, allow nulls
    column status should have allowed values {active, inactive}
    """

    report = expect_df(df, expectations)

    assert report.passed is False
    assert len(report.column_results) == 3

    id_result = next(result for result in report.column_results if result.column == "id")
    assert id_result.passed is False
    assert any("unique" in diagnostic for diagnostic in id_result.diagnostics)

    age_result = next(result for result in report.column_results if result.column == "age")
    assert age_result.passed is False
    assert any("integer" in diagnostic for diagnostic in age_result.diagnostics)

    status_result = next(
        result for result in report.column_results if result.column == "status"
    )
    assert status_result.passed is False
    assert any("unexpected values" in diagnostic for diagnostic in status_result.diagnostics)


def test_expect_df_reports_row_rules_and_formats():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "placed_at": ["2024-01-01", "2024-01-02", "2024-13-01"],
            "code": ["AB12", "ZZ99", "bad"],
            "amount": [10.0, 0.0, -5.0],
        }
    )

    expectations = [
        "expect column order_id to be unique and not null",
        "column placed_at: datetime format %Y-%m-%d",
        "column code should match regex ^[A-Z]{2}\\d{2}$",
        "column amount: float",
    ]

    report = expect_df(df, expectations, row_rules=["rows must satisfy amount >= 0"])

    assert report.passed is False

    placed_at = next(result for result in report.column_results if result.column == "placed_at")
    assert placed_at.passed is False
    assert any("datetime" in diagnostic for diagnostic in placed_at.diagnostics)

    code = next(result for result in report.column_results if result.column == "code")
    assert code.passed is False
    assert any("regex" in diagnostic for diagnostic in code.diagnostics)

    row_rule = report.row_results[0]
    assert row_rule.passed is False
    assert row_rule.failing_indices == [2]
