# ----------------------------------------------------------------------
# ConfDB virtual router <name> route inet syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ....defs import DEF
from ....patterns import IPv4_PREFIX, IPv4_ADDRESS

VR_ROUTE_INET_SYNTAX = DEF(
    "inet",
    [
        DEF(
            "static",
            [
                DEF(
                    IPv4_PREFIX,
                    [
                        DEF(
                            "next-hop",
                            [
                                DEF(
                                    IPv4_ADDRESS,
                                    multi=True,
                                    name="next_hop",
                                    gen="make_inet_static_route_next_hop",
                                )
                            ],
                        ),
                        DEF("discard", gen="make_inet_static_route_discard"),
                    ],
                    name="route",
                )
            ],
        )
    ],
)
