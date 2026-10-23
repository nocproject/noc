# ----------------------------------------------------------------------
# ConfDB virtual-router <name> protocols mpls syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ....defs import DEF
from ....patterns import UNIT_NAME, ANY, INTEGER, IP_ADDRESS

MPLS_SYNTAX = DEF(
    "mpls",
    [
        DEF(
            "admin-groups",
            [
                DEF(
                    ANY,
                    [DEF(INTEGER, name="value", required=True, gen="make_mpls_admin_group")],
                    name="name",
                    multi=True,
                )
            ],
        ),
        DEF(
            "srlg",
            [
                DEF(
                    ANY,
                    [
                        DEF(
                            "value",
                            [DEF(INTEGER, name="value", required=True, gen="make_mpls_srlg_value")],
                        ),
                        DEF(
                            "cost",
                            [DEF(INTEGER, name="cost", required=True, gen="make_mpls_srlg_cost")],
                        ),
                    ],
                    name="name",
                    multi=True,
                )
            ],
        ),
        DEF(
            "interface",
            [
                DEF(
                    UNIT_NAME,
                    [
                        DEF(
                            "admin-group",
                            [
                                DEF(
                                    ANY,
                                    name="group",
                                    multi=True,
                                    required=True,
                                    gen="make_mpls_interface_admin_group",
                                )
                            ],
                        ),
                        DEF(
                            "srlg",
                            [
                                DEF(
                                    ANY,
                                    name="group",
                                    multi=True,
                                    required=True,
                                    gen="make_mpls_interface_srlg",
                                )
                            ],
                        ),
                    ],
                    name="interface",
                    required=True,
                    multi=True,
                    gen="make_mpls_interface",
                )
            ],
        ),
        DEF(
            "label-switched-path",
            [
                DEF(
                    ANY,
                    [
                        DEF(
                            "description",
                            [DEF(ANY, name="description", gen="make_mpls_lsp_description")],
                        )
                    ],
                    name="name",
                    multi=True,
                    gen="make_mpls_lsp",
                ),
                DEF(
                    "to",
                    [
                        DEF(
                            IP_ADDRESS,
                            name="address",
                            required=True,
                            gen="make_mpls_lsp_to_address",
                        )
                    ],
                ),
            ],
        ),
    ],
)
