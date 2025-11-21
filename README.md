# analysta 🖇️

[![PyPI - Version](https://img.shields.io/pypi/v/analysta.svg)](https://pypi.org/project/analysta)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/analysta.svg)](https://pypi.org/project/analysta)

**A Python library for comparing pandas DataFrames using primary keys,**
tolerances, and audit-friendly diffs.** Easily detect mismatches,
missing rows, and cell-level changes between two datasets.

-----

## 🧾 Table of Contents

- [Installation](#installation)
- [Quick Example](#quick-example)
- [CLI Usage](#cli-usage)
- [HTML Reports](#html-reports)
- [More Examples](#more-examples)
- [Features](#features)
- [Development](#development)
- [License](#license)

## 🚀 Installation

```bash
pip install analysta
```

Python 3.10 or higher is required.

For a concise import, you can alias the package:

```python
import analysta as nl
```

## ⚡ Quick Example

```python
import analysta as nl
import pandas as pd

# Row 1 exists only in df1, row 4 only in df2
# Row 3 exists in both but has a different price
df1 = pd.DataFrame({"id": [1, 2, 3], "price": [100, 200, 300]})
df2 = pd.DataFrame({"id": [2, 3, 4], "price": [200, 250, 400]})

delta = nl.Delta(df1, df2, keys="id")
print(delta.unmatched_a)         # → id=1
print(delta.unmatched_b)         # → id=4
print(delta.changed("price"))    # → id=3
print(nl.duplicates(df1, column="id"))  # Duplicates by column
```

## 💻 CLI Usage

`analysta` now includes a powerful CLI for quick comparisons directly from your terminal.

```bash
# Compare two CSV files
analysta diff data/a.csv data/b.csv --key id

# Generate an HTML report
analysta diff data/a.csv data/b.csv --key id --out report.html

# Check version
analysta version
```

## 📊 HTML Reports

Generate beautiful, shareable HTML reports of your data comparisons.

```python
import analysta as nl
import pandas as pd

df_a = pd.read_csv("data/a.csv")
df_b = pd.read_csv("data/b.csv")

delta = nl.Delta(df_a, df_b, keys="id")

# Generate report
delta.to_html("comparison_report.html")
```

## 📚 More Examples

### Tolerant numeric diffs

```python
import analysta as nl
import pandas as pd

df_a = pd.DataFrame({"id": [1, 2], "value": [100.0, 200.005]})
df_b = pd.DataFrame({"id": [1, 2], "value": [100.0, 200.0]})

delta = nl.Delta(df_a, df_b, keys="id", abs_tol=0.01)
print(delta.changed("value"))  # diff 0.005 < 0.01 → empty

delta = nl.Delta(df_a, df_b, keys="id", abs_tol=0.001)
print(delta.changed("value"))  # diff 0.005 > 0.001 → id=2
```

### Counting duplicates

```python
df = pd.DataFrame({"id": [1, 1, 2, 2, 2]})
print(nl.duplicates(df, column="id", counts=True))
```

> [!NOTE]
> `nl.duplicates` is a short alias for `nl.find_duplicates` so existing code
> keeps working while examples stay concise.

### Trimming whitespace

```python
df = pd.DataFrame({"id": ["1"], "name": [" Alice "]})
clean = nl.trim_whitespace(df)
print(clean)
```

### Working with CSV and Excel files

```python
import analysta as nl

transactions = nl.read_csv("transactions.csv", dtype={"id": "Int64"})
nl.write_csv(transactions, "transactions_clean.csv", index=False)

sales = nl.read_excel("sales.xlsx", sheet_name="Raw")
nl.write_excel(sales, "sales_clean.xlsx", sheet_name="Clean", index=False)
```

> [!TIP]
> Excel support relies on `openpyxl` for `.xlsx` files. Install it with
> `pip install openpyxl` if it is not already available in your environment.

### Auditing data quality

```python
import analysta as nl
import pandas as pd

df = pd.DataFrame(
    {
        "id": [1, 2, 3],
        "age": ["34", 28, None],
        "signup_date": ["2024-01-01", "01/03/2024", "31-12-2023"],
    }
)

issues = nl.audit_dataframe(
    df,
    allow_nulls={"age": False},
    expected_dtypes={"age": "int64"},
    date_formats={"signup_date": ["%Y-%m-%d", "%m/%d/%Y"]},
)
print(issues)
```

## ✨ Features

- Key-based row comparison: `"A not in B"` and vice versa
- Tolerant numeric diffs (absolute & relative)
- Highlight changed columns
- **New!** CLI for terminal-based workflows
- **New!** HTML reporting for easy sharing
- Built for analysts, not just engineers
- Automatic trimming of leading/trailing whitespace
- Detect duplicate rows with optional counts
- CSV and Excel import/export helpers that delegate to pandas
- Data quality audit helpers for nulls, types, and dates

## 🛠️ Development

This project uses modern Python tooling:
- **Ruff** for linting and formatting
- **Mypy** for static type checking
- **Pre-commit** hooks to ensure code quality

## 📄 License

`analysta` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
