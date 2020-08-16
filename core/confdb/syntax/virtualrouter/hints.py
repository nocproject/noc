# ----------------------------------------------------------------------
# ConfDB hints virtual-router syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..defs import DEF
from .interfaces.hints import VIRTUAL_ROUTER_INTERFACES_HINTS_SYNTAX

VIRTUAL_ROUTER_HINTS_SYNTAX = DEF("virtual-router", [VIRTUAL_ROUTER_INTERFACES_HINTS_SYNTAX])
