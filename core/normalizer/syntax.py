# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Normalized config syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import namedtuple


SyntaxDef = namedtuple("SyntaxDef", ["token", "children", "required", "name", "multi", "default", "gen"])


def DEF(token, children=None, required=False, multi=False, name=None, default=None, gen=None):
    return SyntaxDef(token, children, required, name, multi, default, gen)


ANY = None
REST = True
VR_NAME = ANY
FI_NAME = ANY
IF_NAME = ANY
UNIT_NAME = ANY
IF_UNIT_NAME = ANY
IPv4_ADDRESS = ANY
IPv4_PREFIX = ANY
IPv6_ADDRESS = ANY
IPv6_PREFIX = ANY
IP_ADDRESS = ANY
ISO_ADDRESS = ANY
INTEGER = ANY
FLOAT = ANY
BOOL = ANY
ETHER_MODE = ANY
STP_MODE = ANY
HHMM = ANY


def CHOICES(*args):
    return ANY


SYNTAX = [
    DEF("system", [
        DEF("hostname", [
            DEF(ANY, required=True, name="hostname", gen="make_hostname")
        ]),
        DEF("domain-name", [
            DEF(ANY, required=True, name="domain_name", gen="make_domain_name")
        ]),
        DEF("prompt", [
            DEF(ANY, required=True, name="prompt", gen="make_prompt")
        ]),
        DEF("clock", [
            DEF("timezone", [
                DEF(ANY, [
                    DEF("offset", [
                        DEF(HHMM, required=True, name="tz_offset", gen="make_tz_offset")
                    ])
                ], required=True, name="tz_name", gen="make_tz")
            ], required=True)
        ])
    ]),
    DEF("interfaces", [
        DEF(IF_NAME, [
            DEF("description", [
                DEF(ANY, required=True, name="description", gen="make_interface_description")
            ]),
            DEF("admin-status", [
                DEF(BOOL, required=True, name="admin_status", gen="make_interface_admin_status")
            ]),
            DEF("mtu", [
                DEF(INTEGER, required=True, name="mtu", gen="make_interface_mtu")
            ]),
            DEF("speed", [
                DEF(INTEGER, required=True, name="speed", gen="make_interface_speed")
            ]),
            DEF("duplex", [
                DEF(BOOL, required=True, name="duplex", gen="make_interface_duplex")
            ]),
            DEF("flow-control", [
                DEF(BOOL, required=True, name="flow_control", gen="make_interface_flow_control")
            ]),
            DEF("ethernet", [
                DEF("auto-negotiation", [
                    DEF(ETHER_MODE, multi=True, name="mode", gen="make_interface_ethernet_autonegotiation")
                ])
            ]),
            DEF("storm-control", [
                DEF("broadcast", [
                    DEF("level", [
                        DEF(FLOAT, required=True, name="level", gen="make_interface_storm_control_broadcast_level")
                    ])
                ]),
                DEF("multicast", [
                    DEF("level", [
                        DEF(FLOAT, required=True, name="level", gen="make_interface_storm_control_multicast_level")
                    ])
                ]),
                DEF("unicast", [
                    DEF("level", [
                        DEF(FLOAT, required=True, name="level", gen="make_interface_storm_control_unicast_level")
                    ])
                ])
            ])
        ], multi=True, name="interface"),
    ]),
    DEF("protocols", [
        DEF("cdp", [
            DEF("interface", [
                DEF(IF_NAME, multi=True, name="interface", gen="make_cdp_interface")
            ])
        ]),
        DEF("lldp", [
            DEF("interface", [
                DEF(IF_NAME, multi=True, name="interface", gen="make_lldp_interface")
            ])
        ]),
        DEF("udld", [
            DEF("interface", [
                DEF(IF_NAME, multi=True, name="interface", gen="make_udld_interface")
            ])
        ]),
        DEF("spanning-tree", [
            DEF("mode", [
                DEF(CHOICES("stp", "rstp", "mstp", "pvst", "rapid-pvst"), required=True,
                    name="mode", gen="make_spanning_tree_mode")
            ]),
            DEF("instance", [
                DEF(INTEGER, [
                    DEF("bridge-priority", [
                        DEF(INTEGER, required=True,
                            name="priority", gen="make_spanning_tree_instance_bridge_priority")
                    ])
                ], multi=True, name="instance", default="0")
            ]),
            DEF("interface", [
                DEF(IF_NAME, [
                    DEF("cost", [
                        DEF(INTEGER, required=True,
                            name="cost", gen="make_spanning_tree_interface_cost")
                    ]),
                    DEF("bpdu-filter", [
                        DEF(BOOL, required=True, name="enabled", gen="make_spanning_tree_interface_bpdu_filter")
                    ]),
                    DEF("bpdu-guard", [
                        DEF(BOOL, required=True, name="enabled", gen="make_spanning_tree_interface_bpdu_guard")
                    ]),
                    DEF("mode", [
                        DEF(CHOICES("normal", "portfast", "portfast-trunk"), required=True,
                            name="mode", gen="make_spanning_tree_interface_mode")
                    ])
                ], multi=True, name="interface"),
            ])
        ])
    ]),
    DEF("virtual-router", [
        DEF(VR_NAME, [
            DEF("forwarding-instance", [
                DEF(FI_NAME, [
                    DEF("interface", [
                        DEF(IF_NAME, [
                            DEF("unit", [
                                DEF(UNIT_NAME, [
                                    DEF("description", [
                                        DEF(ANY, required=True, name="description", gen="make_unit_description")
                                    ]),
                                    DEF("inet", [
                                        DEF("address", [
                                            DEF(IPv4_PREFIX, multi=True, name="address", gen="make_unit_inet_address")
                                        ])
                                    ]),
                                    DEF("inet6", [
                                        DEF("address", [
                                            DEF(IPv6_PREFIX, multi=True, name="address", gen="make_unit_inet6_address")
                                        ])
                                    ]),
                                    DEF("iso", gen="make_unit_iso"),
                                    DEF("mpls", gen="make_unit_mpls"),
                                    DEF("bridge", [
                                        DEF("port-security", [
                                            DEF("max-mac-count", [
                                                DEF(INTEGER, required=True,
                                                    name="limit", gen="make_unit_port_security_max_mac")
                                            ])
                                        ])
                                    ]),
                                ], multi=True, name="unit", default="0")
                            ])
                        ], required=True, multi=True, name="interface")
                    ]),
                    DEF("route", [
                        DEF("inet", [
                            DEF("static", [
                                DEF(IPv4_PREFIX, [
                                    DEF("next-hop", [
                                        DEF(IPv4_ADDRESS, multi=True, name="next_hop", gen="make_inet_static_route_next_hop")
                                    ])
                                ], name="route")
                            ])
                        ]),
                        DEF("inet6", [
                            DEF("static", [
                                DEF(IPv4_PREFIX, [
                                    DEF("next-hop", [
                                        DEF(IPv6_ADDRESS, multi=True, name="next_hop", gen="make_inet6_static_route_next_hop")
                                    ])
                                ])
                            ])
                        ]),
                    ]),
                    DEF("protocols", [
                        DEF("telnet", gen="make_protocols_telnet"),
                        DEF("ssh", gen="make_protocols_ssh"),
                        DEF("http", gen="make_protocols_http"),
                        DEF("https", gen="make_protocols_https"),
                        DEF("snmp", [
                            DEF("community", [
                                DEF(ANY, [
                                    DEF("level", [
                                        DEF(CHOICES("read-only", "read-write"), required=True,
                                            name="level", gen="make_snmp_community_level")
                                    ], required=True)
                                ], required=True, multi=True, name="community")
                            ]),
                            DEF("trap", [
                                DEF("community", [
                                    DEF(ANY, [
                                        DEF("host", [
                                            DEF(IP_ADDRESS, required=True, multi=True)
                                        ], required=True)
                                    ], required=True, multi=True)
                                ], required=True)
                            ])
                        ]),
                        DEF("isis", [
                            DEF("area", [
                                DEF(ISO_ADDRESS, required=True, multi=True)
                            ]),
                            DEF("interface", [
                                DEF(UNIT_NAME, [
                                    DEF("level", [
                                        DEF(CHOICES("1", "2"), required=True, multi=True)
                                    ])
                                ], required=True, multi=True)
                            ])
                        ]),
                        DEF("ospf", [
                            DEF("interface", [
                                DEF(UNIT_NAME, required=True, multi=True)
                            ])
                        ]),
                        DEF("ldp", [
                            DEF("interface", [
                                DEF(UNIT_NAME, required=True, multi=True)
                            ])
                        ]),
                        DEF("rsvp", [
                            DEF("interface", [
                                DEF(UNIT_NAME, required=True, multi=True)
                            ])
                        ]),
                        DEF("pim", [
                            DEF("mode", [
                                DEF(CHOICES("sparse", "dense", "sparse-dense"), required=True),
                            ], required=True),
                            DEF("interface", [
                                DEF(UNIT_NAME, required=True, multi=True)
                            ])
                        ]),
                        DEF("igmp-snooping", [
                            DEF("vlan", [
                                DEF(INTEGER, [
                                    DEF("version", [
                                        DEF(CHOICES("1", "2", "3"), required=True)
                                    ]),
                                    DEF("immediate-leave"),
                                    DEF("interface", [
                                        DEF(UNIT_NAME, [
                                            DEF("multicast-router")
                                        ], multi=True),
                                    ])
                                ], multi=True)
                            ])
                        ])
                    ])
                ], required=True, multi=True, name="instance", default="default")
            ], required=True)
        ], required=True, multi=True, name="vr", default="default")
    ])
]
