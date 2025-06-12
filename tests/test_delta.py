import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from analysta import Delta


def test_changed_returns_only_modified_rows():
    df_a = pd.DataFrame({"id": [1, 2], "price": [100, 200]})
    df_b = pd.DataFrame({"id": [1, 2], "price": [100, 250]})

    delta = Delta(df_a, df_b, keys="id")
    result = delta.changed("price").reset_index(drop=True)

    expected = pd.DataFrame({"id": [2], "price_a": [200], "price_b": [250]})
    pd.testing.assert_frame_equal(result, expected)


def test_whitespace_is_trimmed():
    df_a = pd.DataFrame({"id": [" 1"], "name": ["Alice "]})
    df_b = pd.DataFrame({"id": ["1"], "name": ["Alice"]})

    delta = Delta(df_a, df_b, keys="id")

    assert delta.unmatched_a.empty
    assert delta.unmatched_b.empty
    assert delta.mismatches.empty

