# ----------------------------------------------------------------------
# ConfDB interfaces syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
# NOC modules
from ..defs import DEF
from ..patterns import ANY, CHOICES, IF_NAME, INTEGER, BOOL, FLOAT, ETHER_MODE
from ..meta.interfaces import INTERFACES_META_SYNTAX

INTERFACES_SYNTAX = DEF(
    "interfaces",
    [
        DEF(
            IF_NAME,
            [
                INTERFACES_META_SYNTAX,
                DEF(
                    "type",
                    [
                        DEF(
                            CHOICES(
                                "physical",
                                "SVI",
                                "aggregated",
                                "loopback",
                                "management",
                                "null",
                                "tunnel",
                                "other",
                                "template",
                                "dry",
                                "unknown",
                            ),
                            required=True,
                            name="type",
                            gen="make_interface_type",
                        )
                    ],
                ),
                DEF(
                    "description",
                    [DEF(ANY, required=True, name="description", gen="make_interface_description")],
                ),
                DEF(
                    "admin-status",
                    [
                        DEF(
                            BOOL,
                            required=True,
                            name="admin_status",
                            gen="make_interface_admin_status",
                        )
                    ],
                ),
                DEF("mtu", [DEF(INTEGER, required=True, name="mtu", gen="make_interface_mtu")]),
                DEF(
                    "speed", [DEF(INTEGER, required=True, name="speed", gen="make_interface_speed")]
                ),
                DEF(
                    "duplex", [DEF(BOOL, required=True, name="duplex", gen="make_interface_duplex")]
                ),
                DEF(
                    "flow-control",
                    [
                        DEF(
                            BOOL,
                            required=True,
                            name="flow_control",
                            gen="make_interface_flow_control",
                        )
                    ],
                ),
                DEF(
                    "ethernet",
                    [
                        DEF(
                            "auto-negotiation",
                            [
                                DEF(
                                    ETHER_MODE,
                                    multi=True,
                                    name="mode",
                                    gen="make_interface_ethernet_autonegotiation",
                                )
                            ],
                        )
                    ],
                ),
                DEF(
                    "storm-control",
                    [
                        DEF(
                            "broadcast",
                            [
                                DEF(
                                    "level",
                                    [
                                        DEF(
                                            FLOAT,
                                            required=True,
                                            name="level",
                                            gen="make_interface_storm_control_broadcast_level",
                                        )
                                    ],
                                )
                            ],
                        ),
                        DEF(
                            "multicast",
                            [
                                DEF(
                                    "level",
                                    [
                                        DEF(
                                            FLOAT,
                                            required=True,
                                            name="level",
                                            gen="make_interface_storm_control_multicast_level",
                                        )
                                    ],
                                )
                            ],
                        ),
                        DEF(
                            "unicast",
                            [
                                DEF(
                                    "level",
                                    [
                                        DEF(
                                            FLOAT,
                                            required=True,
                                            name="level",
                                            gen="make_interface_storm_control_unicast_level",
                                        )
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
            ],
            multi=True,
            name="interface",
            gen="make_interface",
        )
    ],
)
