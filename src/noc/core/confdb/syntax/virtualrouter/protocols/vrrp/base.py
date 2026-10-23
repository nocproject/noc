# ----------------------------------------------------------------------
# ConfDB virtual-router <name> protocols vrrp syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ....defs import DEF
from ....patterns import ANY, INTEGER, IP_ADDRESS, UNIT_NAME, BOOL

VRRP_SYNTAX = DEF(
    "vrrp",
    [
        DEF(
            "group",
            [
                DEF(
                    ANY,
                    [
                        DEF("description", [DEF(ANY, name="description", gen="make_vrrp_group")]),
                        DEF(
                            "virtual-address",
                            [
                                DEF(
                                    "inet",
                                    [DEF(IP_ADDRESS, name="address", gen="make_vrrp_address")],
                                ),
                                DEF(
                                    "inet6",
                                    [DEF(IP_ADDRESS, name="address", gen="make_vrrp_address6")],
                                ),
                            ],
                        ),
                        DEF(
                            "interface",
                            [DEF(UNIT_NAME, name="interface", gen="make_vrrp_interface")],
                        ),
                        DEF("priority", [DEF(INTEGER, name="priority", gen="make_vrrp_priority")]),
                        DEF(
                            "authentication",
                            [
                                DEF(
                                    "plain-text",
                                    [
                                        DEF(
                                            "key",
                                            [DEF(ANY, name="key", gen="make_vrrp_plain_key")],
                                        )
                                    ],
                                ),
                                DEF(
                                    "md5",
                                    [DEF("key", [DEF(ANY, name="key", gen="make_vrrp_md5_key")])],
                                ),
                            ],
                        ),
                        DEF(
                            "timers",
                            [
                                DEF(
                                    "advertise-interval",
                                    [
                                        DEF(
                                            INTEGER,
                                            name="interval",
                                            gen="make_vrrp_advertise_interval",
                                        )
                                    ],
                                )
                            ],
                        ),
                        DEF(
                            "preempt",
                            [
                                DEF(
                                    "enabled", [DEF(BOOL, name="enabled", gen="make_vrrp_preempt")]
                                ),
                                DEF(
                                    "timer",
                                    [DEF(INTEGER, name="timer", gen="make_vrrp_preempt_timer")],
                                ),
                            ],
                        ),
                    ],
                    name="group",
                    multi=True,
                    required=True,
                )
            ],
            required=True,
        )
    ],
)
