# ----------------------------------------------------------------------
# ConfDB virtual-router <name> protocols snmp syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ....defs import DEF
from ....patterns import ANY, CHOICES, IP_ADDRESS

SNMP_SYNTAX = DEF(
    "snmp",
    [
        DEF(
            "community",
            [
                DEF(
                    ANY,
                    [
                        DEF(
                            "level",
                            [
                                DEF(
                                    CHOICES("read-only", "read-write"),
                                    required=True,
                                    name="level",
                                    gen="make_snmp_community_level",
                                )
                            ],
                            required=True,
                        )
                    ],
                    required=True,
                    multi=True,
                    name="community",
                )
            ],
        ),
        DEF(
            "trap",
            [
                DEF(
                    "community",
                    [
                        DEF(
                            ANY,
                            [
                                DEF(
                                    "host",
                                    [DEF(IP_ADDRESS, name="address", required=True, multi=True)],
                                    required=True,
                                )
                            ],
                            name="community",
                            required=True,
                            multi=True,
                        )
                    ],
                    required=True,
                )
            ],
        ),
    ],
)
