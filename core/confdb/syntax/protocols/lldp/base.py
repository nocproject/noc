# ----------------------------------------------------------------------
# ConfDB protocols lldp syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import IF_NAME

PROTOCOLS_LLDP_SYNTAX = DEF(
    "lldp",
    [
        DEF(
            "interface",
            [
                DEF(
                    IF_NAME,
                    [
                        DEF(
                            "admin-status",
                            [
                                DEF("rx", gen="make_lldp_admin_status_rx"),
                                DEF("tx", gen="make_lldp_admin_status_tx"),
                            ],
                        )
                    ],
                    multi=True,
                    name="interface",
                    gen="make_lldp_interface",
                )
            ],
        )
    ],
)
