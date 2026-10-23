# ----------------------------------------------------------------------
# ConfDB hints protocols spanning-tree syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import BOOL, INTEGER, IF_NAME


HINTS_PROTOCOLS_SPANNING_TREE = DEF(
    "spanning-tree",
    [
        DEF(
            "status",
            [DEF(BOOL, name="status", required=True, gen="make_global_spanning_tree_status")],
        ),
        DEF(
            "priority",
            [
                DEF(
                    INTEGER,
                    required=True,
                    name="priority",
                    gen="make_global_spanning_tree_priority",
                )
            ],
        ),
        DEF(
            "interface",
            [
                DEF(
                    IF_NAME,
                    [DEF("off", gen="make_spanning_tree_interface_disable")],
                    multi=True,
                    name="interface",
                )
            ],
        ),
    ],
)
