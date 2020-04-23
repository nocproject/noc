# ----------------------------------------------------------------------
# ConfDB virtual-router <name> protocols isis syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ....defs import DEF
from ....patterns import CHOICES, UNIT_NAME, ISO_ADDRESS

ISIS_SYNTAX = DEF(
    "isis",
    [
        DEF(
            "area", [DEF(ISO_ADDRESS, name="area", required=True, multi=True, gen="make_isis_area")]
        ),
        DEF(
            "interface",
            [
                DEF(
                    UNIT_NAME,
                    [
                        DEF(
                            "level",
                            [
                                DEF(
                                    CHOICES("1", "2"),
                                    name="level",
                                    required=True,
                                    multi=True,
                                    gen="make_isis_level",
                                )
                            ],
                        )
                    ],
                    name="interface",
                    required=True,
                    multi=True,
                    gen="make_isis_interface",
                )
            ],
        ),
    ],
)
