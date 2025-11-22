import typer
import pandas as pd
from pathlib import Path
from typing import List, Optional
from .delta import Delta

app = typer.Typer(help="Analysta: DataFrame Toolkit for Analysts")

@app.command()
def diff(
    file_a: Path = typer.Argument(..., help="Path to the first CSV file"),
    file_b: Path = typer.Argument(..., help="Path to the second CSV file"),
    keys: List[str] = typer.Option(..., "--key", "-k", help="Key column(s) to join on"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Path to save HTML report"),
    abs_tol: float = typer.Option(0.0, help="Absolute tolerance for numeric comparison"),
    rel_tol: float = typer.Option(0.0, help="Relative tolerance for numeric comparison"),
):
    """
    Compare two CSV files and optionally generate an HTML report.
    """
    if not file_a.exists():
        typer.echo(f"Error: {file_a} not found", err=True)
        raise typer.Exit(code=1)
    if not file_b.exists():
        typer.echo(f"Error: {file_b} not found", err=True)
        raise typer.Exit(code=1)

    df_a = pd.read_csv(file_a)
    df_b = pd.read_csv(file_b)

    # Validate keys
    for k in keys:
        if k not in df_a.columns:
            typer.echo(f"Error: Key '{k}' not found in {file_a}", err=True)
            raise typer.Exit(code=1)
        if k not in df_b.columns:
            typer.echo(f"Error: Key '{k}' not found in {file_b}", err=True)
            raise typer.Exit(code=1)

    delta = Delta(df_a, df_b, keys=keys, abs_tol=abs_tol, rel_tol=rel_tol)

    typer.echo(f"Comparison complete.")
    typer.echo(f"Rows in A only: {len(delta.unmatched_a)}")
    typer.echo(f"Rows in B only: {len(delta.unmatched_b)}")
    typer.echo(f"Mismatches:     {len(delta.mismatches)}")

    if out:
        delta.to_html(str(out))
        typer.echo(f"Report saved to {out}")

@app.command()
def version():
    """
    Show the version of analysta.
    """
    typer.echo("analysta 0.0.7")

@app.command()
def ui():
    """
    Launch the interactive web UI.
    """
    import subprocess
    import sys
    from pathlib import Path
    
    ui_file = Path(__file__).parent / "ui.py"
    typer.echo("🚀 Launching Analysta Web UI...")
    typer.echo("Opening browser at http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(ui_file)])



if __name__ == "__main__":
    app()
