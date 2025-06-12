# SPDX-FileCopyrightText: 2025-present Diego-Ignacio Ortiz <31400790+dunkel000@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

"""Public Analysta interface."""

from .delta import Delta
from .diff import hello, trim_whitespace, find_duplicates
from .__about__ import __version__

__all__ = ["Delta", "hello", "trim_whitespace", "find_duplicates"]
