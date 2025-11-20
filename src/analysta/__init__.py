# SPDX-FileCopyrightText: 2025-present Diego-Ignacio Ortiz <31400790+dunkel000@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Public Analysta interface."""

from .delta import Delta
from .diff import hello, trim_whitespace, find_duplicates, duplicates
from .io import read_csv, write_csv, read_excel, write_excel
from .quality import audit_dataframe
from .check import expect_df
from .__about__ import __version__

__all__ = [
    "Delta",
    "hello",
    "trim_whitespace",
    "duplicates",
    "find_duplicates",
    "audit_dataframe",
    "expect_df",
    "read_csv",
    "write_csv",
    "read_excel",
    "write_excel",
]
