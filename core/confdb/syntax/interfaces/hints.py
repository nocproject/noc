# ----------------------------------------------------------------------
# ConfDB hints interfaces syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..defs import DEF
from ..patterns import BOOL

INTERFACES_HINTS_SYNTAX = DEF(
    "interfaces",
    [
        DEF(
            "defaults",
            [
                DEF(
                    "admin-status",
                    [
                        DEF(
                            BOOL,
                            required=True,
                            name="admin_status",
                            gen="make_defaults_interface_admin_status",
                        )
                    ],
                )
            ],
        )
    ],
)
