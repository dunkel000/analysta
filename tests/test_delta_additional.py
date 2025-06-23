import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from analysta import Delta


def test_unmatched_rows_detected():
    df_a = pd.DataFrame({"id": [1, 2], "price": [10, 20]})
    df_b = pd.DataFrame({"id": [2, 3], "price": [20, 30]})
    delta = Delta(df_a, df_b, keys="id")

    expected_a = pd.DataFrame({"id": [1], "price_a": [10.0], "price_b": [np.nan]})
    expected_b = pd.DataFrame({"id": [3], "price_a": [np.nan], "price_b": [30.0]})

    pd.testing.assert_frame_equal(delta.unmatched_a.reset_index(drop=True), expected_a)
    pd.testing.assert_frame_equal(delta.unmatched_b.reset_index(drop=True), expected_b)
    assert delta.mismatches.empty


def test_numeric_tolerance():
    df_a = pd.DataFrame({"id": [1, 2], "value": [100.0, 200.005]})
    df_b = pd.DataFrame({"id": [1, 2], "value": [100.0, 200.0]})
    delta = Delta(df_a, df_b, keys="id", abs_tol=0.01)

    assert delta.mismatches.empty
