"""Utility helpers for :mod:`analysta`."""

from __future__ import annotations

import pandas as pd


def hello() -> None:
    """Print a friendly greeting."""

    print("Hello, Analysta!")


def trim_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Return *df* with leading/trailing whitespace stripped from strings."""

    return df.map(lambda x: x.strip() if isinstance(x, str) else x)
