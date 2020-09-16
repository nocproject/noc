# ----------------------------------------------------------------------
# ConfDB hints system aaa
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import IF_NAME, IP_ADDRESS, CHOICES

HINTS_SYSTEM_AAA = DEF(
    "aaa",
    [
        DEF(
            "service-type",
            [
                DEF(
                    CHOICES("local", "radius", "tacacs+", "ldap", "ad"),
                    [
                        DEF(
                            "default-address",
                            [DEF(IP_ADDRESS, name="ip", gen="make_system_aaa_default_address")],
                        ),
                        DEF(
                            "default-interface",
                            [
                                DEF(
                                    IF_NAME,
                                    name="interface",
                                    gen="make_system_aaa_default_interface",
                                )
                            ],
                        ),
                    ],
                    name="type",
                    required=True,
                )
            ],
        ),
    ],
)
