# ----------------------------------------------------------------------
# ConfDB protocols ntp syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import ANY, CHOICES, IP_ADDRESS, INTEGER

PROTOCOLS_NTP_SYNTAX = DEF(
    "ntp",
    [
        DEF(
            ANY,
            [
                DEF(
                    "version",
                    [
                        DEF(
                            CHOICES("1", "2", "3", "4"),
                            required=True,
                            name="version",
                            gen="make_ntp_server_version",
                        )
                    ],
                ),
                DEF(
                    "address",
                    [DEF(IP_ADDRESS, name="address", required=True, gen="make_ntp_server_address")],
                ),
                DEF(
                    "mode",
                    [
                        DEF(
                            CHOICES("client", "server", "peer"),
                            name="mode",
                            required=True,
                            gen="make_ntp_server_mode",
                        )
                    ],
                ),
                DEF(
                    "authentication",
                    [
                        DEF(
                            "type",
                            [
                                DEF(
                                    CHOICES("md5"),
                                    name="auth_type",
                                    required=True,
                                    gen="make_ntp_server_authentication_type",
                                )
                            ],
                        ),
                        DEF(
                            "key",
                            [
                                DEF(
                                    ANY,
                                    name="key",
                                    required=True,
                                    gen="make_ntp_server_authentication_key",
                                )
                            ],
                        ),
                    ],
                ),
                DEF("prefer", gen="make_ntp_server_prefer"),
                DEF(
                    "broadcast",
                    [
                        DEF(
                            "version",
                            [
                                DEF(
                                    CHOICES("1", "2", "3", "4"),
                                    required=True,
                                    name="version",
                                    gen="make_ntp_server_broadcast_version",
                                )
                            ],
                        ),
                        DEF(
                            "address",
                            [
                                DEF(
                                    IP_ADDRESS,
                                    name="address",
                                    required=True,
                                    gen="make_ntp_server_broadcast_address",
                                )
                            ],
                        ),
                        DEF(
                            "ttl",
                            [
                                DEF(
                                    INTEGER,
                                    name="ttl",
                                    required=True,
                                    gen="make_ntp_server_broadcast_ttl",
                                )
                            ],
                        ),
                        DEF(
                            "authentication",
                            [
                                DEF(
                                    "type",
                                    [
                                        DEF(
                                            CHOICES("md5"),
                                            name="auth_type",
                                            required=True,
                                            gen="make_ntp_server_broadcast_authentication_type",
                                        )
                                    ],
                                ),
                                DEF(
                                    "key",
                                    [
                                        DEF(
                                            ANY,
                                            name="key",
                                            required=True,
                                            gen="make_ntp_server_broadcast_authentication_key",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            multi=True,
            name="name",
            gen="make_ntp_server",
        ),
        DEF("boot-server", [DEF(ANY, name="boot_server", gen="make_ntp_boot_server")]),
    ],
)
