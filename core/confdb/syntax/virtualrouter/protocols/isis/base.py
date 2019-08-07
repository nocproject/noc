# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB virtual-router <name> protocols isis syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from ....defs import DEF
from ....patterns import CHOICES, UNIT_NAME, ISO_ADDRESS

ISIS_SYNTAX = DEF(
    "isis",
    [
        DEF("area", [DEF(ISO_ADDRESS, required=True, multi=True)]),
        DEF(
            "interface",
            [
                DEF(
                    UNIT_NAME,
                    [DEF("level", [DEF(CHOICES("1", "2"), required=True, multi=True)])],
                    required=True,
                    multi=True,
                )
            ],
        ),
    ],
)
