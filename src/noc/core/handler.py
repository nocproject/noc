# ----------------------------------------------------------------------
#  Handler management utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any

# Third-party modules
from gufo.loader import ImportPathResolver

# Fallback get_handler. Should be eventually replaced with
# properly-typed handlers.
get_handler = ImportPathResolver[Any]()
