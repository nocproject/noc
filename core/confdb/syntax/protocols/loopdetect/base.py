# ----------------------------------------------------------------------
# ConfDB protocols loop-detect syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import IF_NAME

PROTOCOLS_LOOP_DETECT_SYNTAX = DEF(
    "loop-detect",
    [
        DEF(
            "interface",
            [DEF(IF_NAME, multi=True, name="interface", gen="make_loop_detect_interface")],
        )
    ],
)
