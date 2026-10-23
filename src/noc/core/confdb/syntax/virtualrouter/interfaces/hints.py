# ----------------------------------------------------------------------
# ConfDB hints virtual-router interfaces syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import IF_NAME

VIRTUAL_ROUTER_INTERFACES_HINTS_SYNTAX = DEF(
    "interfaces",
    [
        DEF(
            "untagged",
            [
                DEF(
                    "default",
                    [
                        DEF(
                            IF_NAME,
                            [DEF("off", gen="make_virtual_router_interface_untagged_disabled")],
                            multi=True,
                            name="interface",
                        )
                    ],
                ),
            ],
        ),
    ],
)
