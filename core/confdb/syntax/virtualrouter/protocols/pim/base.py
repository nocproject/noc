# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB virtual-router <name> protocols pim syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from ....defs import DEF
from ....patterns import CHOICES, UNIT_NAME

PIM_SYNTAX = DEF(
    "pim",
    [
        DEF(
            "mode", [DEF(CHOICES("sparse", "dense", "sparse-dense"), required=True)], required=True
        ),
        DEF("interface", [DEF(UNIT_NAME, required=True, multi=True)]),
    ],
)
