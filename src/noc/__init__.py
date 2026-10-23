# ----------------------------------------------------------------------
#  Handler management utilities
# ----------------------------------------------------------------------
# TESTS: ALLOW_NON_EMPTY_INIT
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

"""
NOC main module.

Attributes:
    __version__: Current version.
"""

# Activate custom module loaders
import noc.core.importer  # noqa

__version__: str = "26-dev"

__all__ = ["__version__"]
