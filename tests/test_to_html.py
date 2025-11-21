import pandas as pd
import analysta as nl

def test_to_html_generation():
    df_a = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    df_b = pd.DataFrame({"id": [1, 2], "val": [10, 25]})
    
    delta = nl.Delta(df_a, df_b, keys="id")
    html = delta.to_html()
    
    assert "<!DOCTYPE html>" in html
    assert "Analysta Delta Report" in html
    assert "Mismatches (Top 50)" in html
    assert "<td>20</td>" in html  # val_a
    assert "<td>25</td>" in html  # val_b
