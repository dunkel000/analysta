import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from analysta import duplicates, find_duplicates


@pytest.mark.parametrize("func", [find_duplicates, duplicates])
def test_find_duplicates_returns_rows(func):
    df = pd.DataFrame({"id": [1, 1, 2], "val": [10, 10, 20]})
    result = func(df)
    expected = pd.DataFrame({"id": [1, 1], "val": [10, 10]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


@pytest.mark.parametrize("func", [find_duplicates, duplicates])
def test_find_duplicates_counts(func):
    df = pd.DataFrame({"id": [1, 1, 2, 2, 2]})
    result = func(df, column="id", counts=True)
    expected = pd.DataFrame({"id": [1, 2], "count": [2, 3]})
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.parametrize("func", [find_duplicates, duplicates])
def test_find_duplicates_uses_all_columns_when_column_none(func):
    df = pd.DataFrame(
        {
            "id": [1, 1, 1],
            "val": [10, 10, 10],
            "note": ["alpha", "alpha", "beta"],
        }
    )

    result = func(df)
    expected = pd.DataFrame(
        {
            "id": [1, 1],
            "val": [10, 10],
            "note": ["alpha", "alpha"],
        }
    )

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


@pytest.mark.parametrize("func", [find_duplicates, duplicates])
def test_find_duplicates_preserves_non_subset_columns(func):
    df = pd.DataFrame(
        {
            "id": [1, 1, 2],
            "city": ["NY", "SF", "LA"],
            "value": [100, 200, 300],
        }
    )

    result = func(df, column="id")
    expected = pd.DataFrame(
        {
            "id": [1, 1],
            "city": ["NY", "SF"],
            "value": [100, 200],
        }
    )

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)
