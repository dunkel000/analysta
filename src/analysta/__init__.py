# SPDX-FileCopyrightText: 2025-present Diego-Ignacio Ortiz <31400790+dunkel000@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

from .diff import hello        # src/analysta/__init__.py
__all__ = ["hello"]

"""Public Analysta interface"""
from .delta import Delta

__all__: list[str] = ["Delta"]
__version__: str = "0.0.1"
