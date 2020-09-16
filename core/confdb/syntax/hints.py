# ----------------------------------------------------------------------
# ConfDB hints syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .defs import DEF
from .interfaces.hints import INTERFACES_HINTS_SYNTAX
from .protocols.hints import PROTOCOLS_HINTS_SYNTAX
from .system.hints import SYSTEM_HINTS_SYNTAX
from .virtualrouter.hints import VIRTUAL_ROUTER_HINTS_SYNTAX

HINTS_SYNTAX = DEF(
    "hints",
    [
        INTERFACES_HINTS_SYNTAX,
        PROTOCOLS_HINTS_SYNTAX,
        VIRTUAL_ROUTER_HINTS_SYNTAX,
        SYSTEM_HINTS_SYNTAX,
    ],
)
