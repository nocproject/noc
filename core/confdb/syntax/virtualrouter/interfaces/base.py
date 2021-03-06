# ----------------------------------------------------------------------
# ConfDB virtual router <name> interfaces syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import ANY, INTEGER, CHOICES, IF_NAME, UNIT_NAME, IPv4_PREFIX, IPv6_PREFIX

VR_INTERFACES_SYNTAX = DEF(
    "interfaces",
    [
        DEF(
            IF_NAME,
            [
                DEF(
                    "unit",
                    [
                        DEF(
                            UNIT_NAME,
                            [
                                DEF(
                                    "description",
                                    [
                                        DEF(
                                            ANY,
                                            required=True,
                                            name="description",
                                            gen="make_unit_description",
                                        )
                                    ],
                                ),
                                DEF(
                                    "inet",
                                    [
                                        DEF(
                                            "address",
                                            [
                                                DEF(
                                                    IPv4_PREFIX,
                                                    multi=True,
                                                    name="address",
                                                    gen="make_unit_inet_address",
                                                )
                                            ],
                                        )
                                    ],
                                ),
                                DEF(
                                    "inet6",
                                    [
                                        DEF(
                                            "address",
                                            [
                                                DEF(
                                                    IPv6_PREFIX,
                                                    multi=True,
                                                    name="address",
                                                    gen="make_unit_inet6_address",
                                                )
                                            ],
                                        )
                                    ],
                                ),
                                DEF("iso", gen="make_unit_iso"),
                                DEF("mpls", gen="make_unit_mpls"),
                                DEF(
                                    "vlan_ids",
                                    [
                                        DEF(
                                            ANY,
                                            required=True,
                                            multi=True,
                                            name="vlan_id",
                                            gen="make_unit_vlan_id",
                                        )
                                    ],
                                ),
                                DEF(
                                    "bridge",
                                    [
                                        DEF(
                                            "switchport",
                                            [
                                                DEF(
                                                    "untagged",
                                                    [
                                                        DEF(
                                                            ANY,
                                                            required=True,
                                                            multi=True,
                                                            name="vlan_filter",
                                                            gen="make_switchport_untagged",
                                                        )
                                                    ],
                                                ),
                                                DEF(
                                                    "native",
                                                    [
                                                        DEF(
                                                            ANY,
                                                            required=True,
                                                            name="vlan_id",
                                                            gen="make_switchport_native",
                                                        )
                                                    ],
                                                ),
                                                DEF(
                                                    "tagged",
                                                    [
                                                        DEF(
                                                            ANY,
                                                            required=True,
                                                            multi=True,
                                                            name="vlan_filter",
                                                            gen="make_switchport_tagged",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                        DEF(
                                            "port-security",
                                            [
                                                DEF(
                                                    "max-mac-count",
                                                    [
                                                        DEF(
                                                            INTEGER,
                                                            required=True,
                                                            name="limit",
                                                            gen="make_unit_port_security_max_mac",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        DEF(
                                            "input_vlan_map",
                                            [
                                                DEF(
                                                    "stack",
                                                    [
                                                        DEF(
                                                            CHOICES("0", "1", "2"),
                                                            required=True,
                                                            default="0",
                                                            name="stack",
                                                            gen="make_input_vlan_map_stack",
                                                        )
                                                    ],
                                                ),
                                                DEF(
                                                    "outer_vlans",
                                                    [
                                                        DEF(
                                                            ANY,
                                                            required=False,
                                                            multi=True,
                                                            name="vlan_filter",
                                                            gen="make_input_vlan_map_outer_vlans",
                                                        )
                                                    ],
                                                ),
                                                DEF(
                                                    "inner_vlans",
                                                    [
                                                        DEF(
                                                            ANY,
                                                            required=False,
                                                            multi=True,
                                                            name="vlan_filter",
                                                            gen="make_input_vlan_map_inner_vlans",
                                                        )
                                                    ],
                                                ),
                                                DEF(
                                                    "rewrite",
                                                    [
                                                        DEF(
                                                            CHOICES("pop", "push", "swap", "drop"),
                                                            [
                                                                DEF(
                                                                    ANY,
                                                                    name="vlan",
                                                                    required=False,
                                                                    gen="make_input_vlan_map_rewrite_vlan",
                                                                )
                                                            ],
                                                            name="op",
                                                            required=True,
                                                            gen="make_input_vlan_map_rewrite_operation",
                                                        )
                                                    ],
                                                    required=False,
                                                    multi=True,
                                                    name="op_num",
                                                ),
                                            ],
                                            multi=True,
                                            required=True,
                                            name="num",
                                        ),
                                        DEF(
                                            "output_vlan_map",
                                            [
                                                DEF(
                                                    "stack",
                                                    [
                                                        DEF(
                                                            CHOICES("0", "1", "2"),
                                                            required=True,
                                                            default="0",
                                                            name="stack",
                                                            gen="make_output_vlan_map_stack",
                                                        )
                                                    ],
                                                ),
                                                DEF(
                                                    "outer_vlans",
                                                    [
                                                        DEF(
                                                            ANY,
                                                            required=False,
                                                            multi=True,
                                                            name="vlan_filter",
                                                            gen="make_output_vlan_map_outer_vlans",
                                                        )
                                                    ],
                                                ),
                                                DEF(
                                                    "inner_vlans",
                                                    [
                                                        DEF(
                                                            ANY,
                                                            required=False,
                                                            multi=True,
                                                            name="vlan_filter",
                                                            gen="make_output_vlan_map_inner_vlans",
                                                        )
                                                    ],
                                                ),
                                                DEF(
                                                    "rewrite",
                                                    [
                                                        DEF(
                                                            CHOICES("pop", "push", "swap", "drop"),
                                                            [
                                                                DEF(
                                                                    ANY,
                                                                    name="vlan",
                                                                    required=False,
                                                                    gen="make_output_vlan_map_rewrite_vlan",
                                                                )
                                                            ],
                                                            name="op",
                                                            required=True,
                                                            gen="make_output_vlan_map_rewrite_operation",
                                                        )
                                                    ],
                                                    required=False,
                                                    multi=True,
                                                    name="op_num",
                                                ),
                                            ],
                                            multi=True,
                                            required=True,
                                            name="num",
                                        ),
                                        DEF(
                                            "dynamic_vlans",
                                            [
                                                DEF(
                                                    ANY,
                                                    [
                                                        DEF(
                                                            "service",
                                                            [
                                                                DEF(
                                                                    CHOICES("voice", "mvr"),
                                                                    name="service",
                                                                    gen="make_interface_serivce_vlan",
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                    multi=True,
                                                    name="vlan_filter",
                                                )
                                            ],
                                            required=False,
                                        ),
                                    ],
                                ),
                            ],
                            multi=True,
                            name="unit",
                            default="0",
                        )
                    ],
                )
            ],
            required=True,
            multi=True,
            name="interface",
        )
    ],
)
