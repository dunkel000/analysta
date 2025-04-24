# analysta 🖇️

[![PyPI - Version](https://img.shields.io/pypi/v/analysta.svg)](https://pypi.org/project/analysta)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/analysta.svg)](https://pypi.org/project/analysta)

**A Python library for comparing pandas DataFrames using primary keys, tolerances, and audit-friendly diffs.**  
Easily detect mismatches, missing rows, and cell-level changes between two datasets.

-----

## 🧾 Table of Contents

- [Installation](#installation)
- [Quick Example](#quick-example)
- [Features](#features)
- [License](#license)

## 🚀 Installation

```bash
pip install analysta
```

Python 3.9 or higher is required.

## ⚡ Quick Example

```python
from analysta import Delta
import pandas as pd

df1 = pd.DataFrame({"id": [1, 2], "price": [100, 200]})
df2 = pd.DataFrame({"id": [1, 2], "price": [100, 250]})

delta = Delta(df1, df2, keys=["id"])
print(delta.unmatched_a)         # Rows in df1 not in df2
print(delta.unmatched_b)         # Rows in df2 not in df1
print(delta.changed("price"))    # Row(s) where price changed
```

## ✨ Features

- Key-based row comparison: `"A not in B"` and vice versa
- Tolerant numeric diffs (absolute & relative)
- Highlight changed columns
- Built for analysts, not just engineers
- CLI and HTML reporting coming soon

## 📄 License

`analysta` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
