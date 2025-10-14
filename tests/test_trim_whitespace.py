import os
import sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from analysta import trim_whitespace


def test_trim_whitespace_removes_spaces():
    df = pd.DataFrame({"a": [" x ", "y"], "b": [1, 2]})
    result = trim_whitespace(df)
    expected = pd.DataFrame({"a": ["x", "y"], "b": [1, 2]})
    pd.testing.assert_frame_equal(result, expected)


def test_trim_whitespace_preserves_non_string_objects():
    df = pd.DataFrame({"mixed": [" value ", 10, None], "num": [1, 2, 3]})

    result = trim_whitespace(df)

    expected = pd.DataFrame({"mixed": ["value", 10, None], "num": [1, 2, 3]})
    pd.testing.assert_frame_equal(result, expected)
