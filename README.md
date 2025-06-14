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
- [More Examples](#more-examples)
- [Features](#features)
- [License](#license)

## 🚀 Installation

```bash
pip install analysta
```

Python 3.8 or higher is required.

## ⚡ Quick Example

```python
from analysta import Delta, find_duplicates
import pandas as pd

df1 = pd.DataFrame({"id": [1, 2], "price": [100, 200]})
df2 = pd.DataFrame({"id": [1, 2], "price": [100, 250]})

delta = Delta(df1, df2, keys=["id"])
print(delta.unmatched_a)         # Rows in df1 not in df2
print(delta.unmatched_b)         # Rows in df2 not in df1
print(delta.changed("price"))    # Row(s) where price changed
print(find_duplicates(df1, column="id"))  # Duplicates by column
```

## 📚 More Examples

### Tolerant numeric diffs

```python
from analysta import Delta, find_duplicates, trim_whitespace
import pandas as pd

df_a = pd.DataFrame({"id": [1, 2], "value": [100.0, 200.005]})
df_b = pd.DataFrame({"id": [1, 2], "value": [100.0, 200.0]})

delta = Delta(df_a, df_b, keys="id", abs_tol=0.01)
print(delta.changed("value"))
```

### Counting duplicates

```python
df = pd.DataFrame({"id": [1, 1, 2, 2, 2]})
print(find_duplicates(df, column="id", counts=True))
```

### Trimming whitespace

```python
df = pd.DataFrame({"id": ["1"], "name": [" Alice "]})
clean = trim_whitespace(df)
print(clean)
```

## ✨ Features

- Key-based row comparison: `"A not in B"` and vice versa
- Tolerant numeric diffs (absolute & relative)
- Highlight changed columns
- Built for analysts, not just engineers
- Automatic trimming of leading/trailing whitespace
- Detect duplicate rows with optional counts
- CLI and HTML reporting coming soon

## 📄 License

`analysta` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
