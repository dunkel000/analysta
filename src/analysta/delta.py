"""
Delta – key-aware DataFrame diff
Copyright (c) 2025  MIT License
"""
from __future__ import annotations

from .diff import trim_whitespace

import pandas as pd


class Delta:  # pylint: disable=too-few-public-methods
    """
    Compare two DataFrames on one or many key columns.

    Parameters
    ----------
    df_a, df_b : pandas.DataFrame
        DataFrames to compare.
    keys : str | list[str]
        Column(s) that uniquely identify each row.
    abs_tol, rel_tol : float, default 0
        Absolute / relative numeric tolerance when checking for equality.
    """

    def __init__(
        self,
        df_a: pd.DataFrame,
        df_b: pd.DataFrame,
        keys: str | list[str],
        *,
        abs_tol: float = 0.0,
        rel_tol: float = 0.0,
    ) -> None:
        self.df_a = trim_whitespace(df_a.copy())
        self.df_b = trim_whitespace(df_b.copy())
        self.keys = [keys] if isinstance(keys, str) else list(keys)
        self.abs_tol = abs_tol
        self.rel_tol = rel_tol

        self._build_diff_frames()

    # --------------------------------------------------------------------- #
    # Public attributes filled by _build_diff_frames()
    #
    unmatched_a: pd.DataFrame  # rows in A but not in B
    unmatched_b: pd.DataFrame  # rows in B but not in A
    mismatches: pd.DataFrame   # aligned rows whose non-key columns differ
    # --------------------------------------------------------------------- #

    # ------------------------ public helpers ----------------------------- #
    def changed(self, column: str) -> pd.DataFrame:
        """Return rows where *column* differs between A and B."""
        col_a = f"{column}_a"
        col_b = f"{column}_b"
        return self.mismatches[self.keys + [col_a, col_b]]

    # ------------------------ internal logic ----------------------------- #
    def _build_diff_frames(self) -> None:
        # Outer merge tells us where rows exist
        merged = self.df_a.merge(
            self.df_b,
            on=self.keys,
            how="outer",
            suffixes=("_a", "_b"),
            indicator=True,
        )

        # A ⧵ B  and  B ⧵ A
        self.unmatched_a = merged.query("_merge == 'left_only'").drop(columns="_merge")
        self.unmatched_b = merged.query("_merge == 'right_only'").drop(columns="_merge")

        # Rows present in both → look for cell differences
        both = merged.query("_merge == 'both'").drop(columns="_merge").copy()

        diff_mask = pd.Series(False, index=both.index)
        for base in (c[:-2] for c in both.columns if c.endswith("_a")):
            col_a, col_b = f"{base}_a", f"{base}_b"
            if pd.api.types.is_numeric_dtype(both[col_a]):
                equal_num = (
                    (both[col_a] - both[col_b]).abs()
                    <= self.abs_tol + self.rel_tol * both[col_b].abs()
                )
                diff_mask |= ~equal_num
            else:
                diff_mask |= both[col_a] != both[col_b]

        self.mismatches = both.loc[diff_mask].reset_index(drop=True)

    # ------------------------ dunder sugar ------------------------------- #
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Delta unmatched_a={len(self.unmatched_a)}, "
            f"unmatched_b={len(self.unmatched_b)}, "
            f"mismatches={len(self.mismatches)}>"
        )

