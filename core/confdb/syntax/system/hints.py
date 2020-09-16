# ----------------------------------------------------------------------
# ConfDB hints system syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..defs import DEF
from .aaa.hints import HINTS_SYSTEM_AAA

SYSTEM_HINTS_SYNTAX = DEF("system", [HINTS_SYSTEM_AAA])
