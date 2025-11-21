from typer.testing import CliRunner
from analysta.cli import app
import pandas as pd
import os

runner = CliRunner()

def test_cli_diff(tmp_path):
    df_a = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    df_b = pd.DataFrame({"id": [1, 2], "val": [10, 25]})
    
    file_a = tmp_path / "a.csv"
    file_b = tmp_path / "b.csv"
    df_a.to_csv(file_a, index=False)
    df_b.to_csv(file_b, index=False)
    
    result = runner.invoke(app, ["diff", str(file_a), str(file_b), "--key", "id"])
    assert result.exit_code == 0
    assert "Comparison complete" in result.stdout
    assert "Mismatches:     1" in result.stdout

def test_cli_html_report(tmp_path):
    df_a = pd.DataFrame({"id": [1], "val": [10]})
    df_b = pd.DataFrame({"id": [1], "val": [20]})
    
    file_a = tmp_path / "a.csv"
    file_b = tmp_path / "b.csv"
    df_a.to_csv(file_a, index=False)
    df_b.to_csv(file_b, index=False)
    
    report_path = tmp_path / "report.html"
    
    result = runner.invoke(app, ["diff", str(file_a), str(file_b), "--key", "id", "--out", str(report_path)])
    assert result.exit_code == 0
    assert report_path.exists()
    assert "Analysta Delta Report" in report_path.read_text()
