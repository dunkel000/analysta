import pandas as pd
import pandas.testing as pdt
import pytest

from analysta.io import read_csv, write_csv, read_excel, write_excel


def test_csv_round_trip(tmp_path):
    dataframe = pd.DataFrame({"id": [1, 2], "value": [10.5, 20.75]})
    csv_path = tmp_path / "sample.csv"

    write_csv(dataframe, csv_path, index=False)

    result = read_csv(csv_path, dtype={"id": "int64"})

    pdt.assert_frame_equal(result, dataframe)
    assert str(result["id"].dtype) == "int64"


def test_write_csv_invalid_option(tmp_path):
    dataframe = pd.DataFrame({"id": [1]})

    with pytest.raises(TypeError):
        write_csv(dataframe, tmp_path / "bad.csv", invalid_kw=True)


def test_excel_round_trip(tmp_path):
    pytest.importorskip("openpyxl")

    dataframe = pd.DataFrame({"id": [1, 2], "label": ["a", "b"]})
    excel_path = tmp_path / "sample.xlsx"

    write_excel(dataframe, excel_path, sheet_name="Data", index=False)

    result = read_excel(excel_path, sheet_name="Data")

    pdt.assert_frame_equal(result, dataframe)
