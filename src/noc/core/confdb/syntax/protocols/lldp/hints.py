# ----------------------------------------------------------------------
# ConfDB hints protocols lldp syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import BOOL, IF_NAME

HINTS_PROTOCOLS_LLDP = DEF(
    "lldp",
    [
        DEF("status", [DEF(BOOL, name="status", required=True, gen="make_global_lldp_status")]),
        DEF(
            "interface",
            [
                DEF(
                    IF_NAME,
                    [DEF("off", gen="make_lldp_interface_disable")],
                    multi=True,
                    name="interface",
                )
            ],
        ),
    ],
)
