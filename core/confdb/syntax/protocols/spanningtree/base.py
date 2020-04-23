# ----------------------------------------------------------------------
# ConfDB protocols spanning-tree syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import CHOICES, INTEGER, BOOL, IF_NAME

PROTOCOLS_SPANNING_TREE_SYNTAX = DEF(
    "spanning-tree",
    [
        DEF(
            "mode",
            [
                DEF(
                    CHOICES("stp", "rstp", "mstp", "pvst", "rapid-pvst"),
                    required=True,
                    name="mode",
                    gen="make_spanning_tree_mode",
                )
            ],
        ),
        DEF(
            "priority",
            [DEF(INTEGER, name="priority", required=True, gen="make_spanning_tree_priority")],
        ),
        DEF(
            "instance",
            [
                DEF(
                    INTEGER,
                    [
                        DEF(
                            "bridge-priority",
                            [
                                DEF(
                                    INTEGER,
                                    required=True,
                                    name="priority",
                                    gen="make_spanning_tree_instance_bridge_priority",
                                )
                            ],
                        )
                    ],
                    multi=True,
                    name="instance",
                    default="0",
                )
            ],
        ),
        DEF(
            "interface",
            [
                DEF(
                    IF_NAME,
                    [
                        DEF(
                            "admin-status",
                            [
                                DEF(
                                    BOOL,
                                    required=True,
                                    name="admin_status",
                                    gen="make_interface_spanning_tree_admin_status",
                                )
                            ],
                        ),
                        DEF(
                            "cost",
                            [
                                DEF(
                                    INTEGER,
                                    required=True,
                                    name="cost",
                                    gen="make_spanning_tree_interface_cost",
                                )
                            ],
                        ),
                        DEF(
                            "bpdu-filter",
                            [
                                DEF(
                                    BOOL,
                                    required=True,
                                    name="enabled",
                                    gen="make_spanning_tree_interface_bpdu_filter",
                                )
                            ],
                        ),
                        DEF(
                            "bpdu-guard",
                            [
                                DEF(
                                    BOOL,
                                    required=True,
                                    name="enabled",
                                    gen="make_spanning_tree_interface_bpdu_guard",
                                )
                            ],
                        ),
                        DEF(
                            "mode",
                            [
                                DEF(
                                    CHOICES("normal", "portfast", "portfast-trunk"),
                                    required=True,
                                    name="mode",
                                    gen="make_spanning_tree_interface_mode",
                                )
                            ],
                        ),
                    ],
                    multi=True,
                    name="interface",
                )
            ],
        ),
    ],
)
