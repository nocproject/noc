# ----------------------------------------------------------------------
# ConfDB protocols lacp syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import IF_NAME, INTEGER, CHOICES

PROTOCOLS_LACP_SYNTAX = DEF(
    "lacp",
    [
        DEF(
            "interface",
            [
                DEF(
                    IF_NAME,
                    [
                        DEF(
                            "system-id",
                            [
                                DEF(
                                    INTEGER,
                                    required=True,
                                    name="system_id",
                                    gen="make_lacp_interface_system_id",
                                )
                            ],
                        ),
                        DEF(
                            "admin-key",
                            [
                                DEF(
                                    INTEGER,
                                    required=True,
                                    name="key",
                                    gen="make_lacp_interface_admin_key",
                                )
                            ],
                        ),
                        DEF(
                            "interval",
                            [
                                DEF(
                                    INTEGER,
                                    required=True,
                                    name="seconds",
                                    gen="make_lacp_interface_interval",
                                )
                            ],
                        ),
                    ],
                    multi=True,
                    name="lag_name",
                ),
                DEF(
                    IF_NAME,
                    [
                        DEF(
                            "mode",
                            [
                                DEF(
                                    CHOICES("active", "passive"),
                                    required=True,
                                    name="mode",
                                    gen="make_lacp_interface_mode",
                                )
                            ],
                        )
                    ],
                    multi=True,
                    name="member_name",
                ),
            ],
        )
    ],
)
