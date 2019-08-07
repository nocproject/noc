# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB virtual-router <name> protocols igmp-snooping syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from ....defs import DEF
from ....patterns import CHOICES, INTEGER, UNIT_NAME

IGMP_SNOOPING_SYNTAX = DEF(
    "igmp-snooping",
    [
        DEF(
            "vlan",
            [
                DEF(
                    INTEGER,
                    [
                        DEF("version", [DEF(CHOICES("1", "2", "3"), required=True)]),
                        DEF("immediate-leave"),
                        DEF("interface", [DEF(UNIT_NAME, [DEF("multicast-router")], multi=True)]),
                    ],
                    multi=True,
                )
            ],
        )
    ],
)
