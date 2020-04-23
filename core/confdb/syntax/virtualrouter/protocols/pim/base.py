# ----------------------------------------------------------------------
# ConfDB virtual-router <name> protocols pim syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ....defs import DEF
from ....patterns import CHOICES, UNIT_NAME

PIM_SYNTAX = DEF(
    "pim",
    [
        DEF(
            "mode",
            [
                DEF(
                    CHOICES("sparse", "dense", "sparse-dense"),
                    name="mode",
                    required=True,
                    gen="make_pim_mode",
                )
            ],
            required=True,
        ),
        DEF(
            "interface",
            [DEF(UNIT_NAME, name="interface", required=True, multi=True, gen="make_pim_interface")],
        ),
    ],
)
