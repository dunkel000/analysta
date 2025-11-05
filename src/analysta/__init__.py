# SPDX-FileCopyrightText: 2025-present Diego-Ignacio Ortiz <31400790+dunkel000@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Public Analysta interface."""

from .delta import Delta
from .diff import hello, trim_whitespace, find_duplicates
from .io import read_csv, write_csv, read_excel, write_excel
from .quality import audit_dataframe
from .__about__ import __version__

__all__ = [
    "Delta",
    "hello",
    "trim_whitespace",
    "find_duplicates",
    "audit_dataframe",
    "read_csv",
    "write_csv",
    "read_excel",
    "write_excel",
]
