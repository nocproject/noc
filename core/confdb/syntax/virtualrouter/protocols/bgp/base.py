# ----------------------------------------------------------------------
# ConfDB virtual-router <name> protocols bgp syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ....defs import DEF
from ....patterns import ANY, IP_ADDRESS, AS_NUM, CHOICES, BOOL

BGP_SYNTAX = DEF(
    "bgp",
    [
        DEF(
            "peer-groups",
            [DEF(ANY, required=True, name="name", gen="make_bgp_peer_group")],
            multi=True,
        ),
        DEF(
            "networks",
            [DEF(ANY, name="prefix", gen="make_bgp_network")],
            multi=True,
        ),
        DEF(
            "policies",
            [DEF(ANY, name="name", gen="make_bgp_policy")],
            multi=True,
        ),
        DEF(
            "neighbors",
            [
                DEF(
                    IP_ADDRESS,
                    [
                        DEF(
                            "type",
                            [
                                DEF(
                                    CHOICES("internal", "external"),
                                    name="type",
                                    required=True,
                                    gen="make_bgp_neighbor_type",
                                )
                            ],
                        ),
                        DEF(
                            "router-id",
                            [
                                DEF(
                                    IP_ADDRESS,
                                    name="router_id",
                                    required=True,
                                    gen="make_bgp_neighbor_router_id",
                                )
                            ],
                        ),
                        DEF(
                            "remote-as",
                            [
                                DEF(
                                    AS_NUM,
                                    name="as_num",
                                    required=True,
                                    gen="make_bgp_neighbor_remote_as",
                                )
                            ],
                            required=True,
                        ),
                        DEF(
                            "admin-status",
                            [
                                DEF(
                                    BOOL,
                                    required=True,
                                    name="admin_status",
                                    gen="make_bgp_neighbor_admin_status",
                                )
                            ],
                        ),
                        DEF(
                            "local-as",
                            [
                                DEF(
                                    AS_NUM,
                                    name="as_num",
                                    required=True,
                                    gen="make_bgp_neighbor_local_as",
                                )
                            ],
                        ),
                        DEF(
                            "local-address",
                            [
                                DEF(
                                    IP_ADDRESS,
                                    name="address",
                                    required=True,
                                    gen="make_bgp_neighbor_local_address",
                                )
                            ],
                        ),
                        DEF(
                            "peer-group",
                            [
                                DEF(
                                    ANY,
                                    name="group",
                                    required=True,
                                    gen="make_bgp_neighbor_peer_group",
                                )
                            ],
                        ),
                        DEF(
                            "description",
                            [
                                DEF(
                                    ANY,
                                    required=True,
                                    name="description",
                                    gen="make_bgp_neighbor_description",
                                )
                            ],
                        ),
                        DEF(
                            "import-filter",
                            [
                                DEF(
                                    ANY,
                                    required=True,
                                    name="name",
                                    gen="make_bgp_neighbor_import_filter",
                                )
                            ],
                        ),
                        DEF(
                            "export-filter",
                            [
                                DEF(
                                    ANY,
                                    required=True,
                                    name="name",
                                    gen="make_bgp_neighbor_export_filter",
                                )
                            ],
                        ),
                        DEF(
                            "redistribute",
                            [
                                DEF(
                                    CHOICES("connected", "static", "bgp", "ospf"),
                                    required=True,
                                    name="type",
                                    gen="make_bgp_neighbor_redistribute",
                                )
                            ],
                            multi=True,
                        ),
                    ],
                    name="neighbor",
                    multi=True,
                    gen="make_bgp_neighbor",
                )
            ],
        ),
    ],
)
