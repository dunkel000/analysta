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


def test_relative_tolerance_allows_proportional_differences():
    df_a = pd.DataFrame({"id": [1, 2], "value": [100.05, 50.0]})
    df_b = pd.DataFrame({"id": [1, 2], "value": [100.0, 50.0]})

    delta = Delta(df_a, df_b, keys="id", rel_tol=0.001)

    assert delta.mismatches.empty


def test_relative_tolerance_detects_excess_difference():
    df_a = pd.DataFrame({"id": [1], "value": [100.25]})
    df_b = pd.DataFrame({"id": [1], "value": [100.0]})

    delta = Delta(df_a, df_b, keys="id", rel_tol=0.001)

    expected = pd.DataFrame({"id": [1], "value_a": [100.25], "value_b": [100.0]})
    pd.testing.assert_frame_equal(delta.mismatches.reset_index(drop=True), expected)


def test_multi_key_comparison_detects_mismatches():
    df_a = pd.DataFrame(
        {
            "id": [1, 1, 2],
            "region": ["NA", "EU", "EU"],
            "value": [10.0, 20.0, 30.0],
            "label": ["ok", "fine", "matched"],
        }
    )
    df_b = pd.DataFrame(
        {
            "id": [1, 1, 2],
            "region": ["NA", "EU", "EU"],
            "value": [10.0, 21.5, 30.0],
            "label": ["ok", "Fine", "matched"],
        }
    )

    delta = Delta(df_a, df_b, keys=["id", "region"])

    expected = pd.DataFrame(
        {
            "id": [1],
            "region": ["EU"],
            "value_a": [20.0],
            "label_a": ["fine"],
            "value_b": [21.5],
            "label_b": ["Fine"],
        }
    )

    pd.testing.assert_frame_equal(delta.mismatches.reset_index(drop=True), expected)
    result = delta.changed("value").reset_index(drop=True)
    pd.testing.assert_frame_equal(
        result,
        expected[["id", "region", "value_a", "value_b"]],
    )
