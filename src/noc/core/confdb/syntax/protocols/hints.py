# ----------------------------------------------------------------------
# ConfDB hints protocols syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..defs import DEF
from .lldp.hints import HINTS_PROTOCOLS_LLDP
from .cdp.hints import HINTS_PROTOCOLS_CDP
from .spanningtree.hints import HINTS_PROTOCOLS_SPANNING_TREE
from .loopdetect.hints import HINTS_PROTOCOLS_LOOP_DETECT

PROTOCOLS_HINTS_SYNTAX = DEF(
    "protocols",
    [
        HINTS_PROTOCOLS_LLDP,
        HINTS_PROTOCOLS_CDP,
        HINTS_PROTOCOLS_SPANNING_TREE,
        HINTS_PROTOCOLS_LOOP_DETECT,
    ],
)
