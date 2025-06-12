import os
import sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from analysta import find_duplicates


def test_find_duplicates_returns_rows():
    df = pd.DataFrame({"id": [1, 1, 2], "val": [10, 10, 20]})
    result = find_duplicates(df)
    expected = pd.DataFrame({"id": [1, 1], "val": [10, 10]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


def test_find_duplicates_counts():
    df = pd.DataFrame({"id": [1, 1, 2, 2, 2]})
    result = find_duplicates(df, column="id", counts=True)
    expected = pd.DataFrame({"id": [1, 2], "count": [2, 3]})
    pd.testing.assert_frame_equal(result, expected)
