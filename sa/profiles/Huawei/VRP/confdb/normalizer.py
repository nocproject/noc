# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Huawei.VRP config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST
from noc.core.confdb.syntax import DEF, IF_NAME, BOOL


class VRPNormalizer(BaseNormalizer):

    SYNTAX = [
        DEF(
            "interfaces",
            [
                DEF(
                    IF_NAME,
                    [
                        DEF(
                            "bpdu",
                            [
                                DEF(
                                    BOOL,
                                    required=False,
                                    name="enabled",
                                    gen="make_interface_ethernet_bpdu",
                                )
                            ],
                        )
                    ],
                    multi=True,
                    name="interface",
                )
            ],
        )
    ]

    @match("sysname", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[1])

    @match("undo", "http", "server", "enable")
    def normalize_http_server(self, tokens):
        yield self.make_protocols_http()

    @match("undo", "http", "secure-server", "enable")
    def normalize_https_server(self, tokens):
        yield self.make_protocols_https()

    @match("aaa", "local-user", ANY, "privilege", "level", ANY)
    def normalize_username_access_level(self, tokens):
        yield self.make_user_class(username=tokens[2], class_name="level-%s" % tokens[5])

    @match("aaa", "local-user", ANY, "password", REST)
    def normalize_username_password(self, tokens):
        yield self.make_user_encrypted_password(username=tokens[2], password=" ".join(tokens[4:]))

    @match("vlan", "batch", REST)
    def normalize_vlan_id_batch(self, tokens):
        for vlan in tokens[2:]:
            yield self.make_vlan_id(vlan_id=vlan)

    @match("vlan", ANY)
    def normalize_vlan_id(self, tokens):
        yield self.make_vlan_id(vlan_id=tokens[1])

    @match("vlan", ANY, "description", REST)
    def normalize_vlan_description(self, tokens):
        yield self.make_vlan_description(vlan_id=tokens[1], description=" ".join(tokens[3:]))

    @match("interface", ANY)
    def normalize_interface(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_interface(interface=if_name)

    @match("interface", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(
            interface=self.interface_name(tokens[1]), description=" ".join(tokens[2:])
        )

    @match("interface", ANY, "port-security", "max-mac-num", ANY)
    def normalize_port_security(self, tokens):
        yield self.make_unit_port_security_max_mac(
            interface=self.interface_name(tokens[1]), limit=tokens[4]
        )

    @match("interface", ANY, "broadcast-suppression", ANY)
    def normalize_port_storm_control_broadcast(self, tokens):
        yield self.make_interface_storm_control_broadcast_level(
            interface=self.interface_name(tokens[1]), level=tokens[3]
        )

    @match("interface", ANY, "multicast-suppression", ANY)
    def normalize_port_storm_control_multicast(self, tokens):
        yield self.make_interface_storm_control_multicast_level(
            interface=self.interface_name(tokens[1]), level=tokens[3]
        )

    @match("interface", ANY, "unicast-suppression", ANY)
    def normalize_port_storm_control_unicast(self, tokens):
        yield self.make_interface_storm_control_unicast_level(
            interface=self.interface_name(tokens[1]), level=tokens[3]
        )

    @match("interface", ANY, "stp", "cost", ANY)
    def normalize_stp_cost(self, tokens):
        yield self.make_spanning_tree_interface_cost(
            interface=self.interface_name(tokens[1]), cost=tokens[4]
        )

    @match("interface", ANY, "port", "hybrid", "pvid", "vlan", ANY)
    def normalize_switchport_untagged(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_switchport_untagged(interface=if_name, unit=if_name, vlan_filter=tokens[6])

    @match("interface", ANY, "port", "trunk", "allow-pass", "vlan", REST)
    def normalize_switchport_tagged(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_switchport_tagged(
            interface=if_name,
            unit=if_name,
            vlan_filter=" ".join(tokens[6:]).replace(" to ", "-").replace(" ", ","),
        )

    @match("interface", ANY, "undo", "negotiation", "auto")
    def normalize_interface_negotiation(self, tokens):
        yield self.make_interface_ethernet_autonegotiation(
            interface=self.interface_name(tokens[1]), mode="manual"
        )

    @match("interface", ANY, "bpdu", "enable")
    def normalize_interface_bpdu(self, tokens):
        yield self.make_interface_ethernet_bpdu(
            interface=self.interface_name(tokens[1]), enabled=True
        )

    @match("interface", ANY, "loopback-detect", "enable")
    def normalize_interface_no_loop_detect(self, tokens):
        if not self.get_context("loop_detect_disabled"):
            if_name = self.interface_name(tokens[1])
            yield self.make_loop_detect_interface(interface=if_name)

    @match("enable", "lldp")
    def normalize_enable_lldp(self, tokens):
        self.set_context("lldp_disabled", False)
        yield self.make_global_lldp_status(status=True)

    @match("enable", "stp")
    def normalize_enable_stp(self, tokens):
        self.set_context("stp_disabled", False)
        yield self.make_global_stp_status(status=True)

    @match("interface", ANY, "undo", "lldp", "enable")
    def normalize_interface_lldp_enable(self, tokens):
        yield self.make_lldp_interface_disable(interface=self.interface_name(tokens[1]))

    @match("interface", ANY, "stp", "disable")
    def normalize_interface_stp_status(self, tokens):
        yield self.make_spanning_tree_interface_disable(interface=self.interface_name(tokens[1]))

    @match("interface", ANY, "stp", "bpdu-filter", "enable")
    def normalize_interface_stp_bpdu_filter(self, tokens):
        yield self.make_spanning_tree_interface_bpdu_filter(
            interface=self.interface_name(tokens[1]), enabled=True
        )

    @match("interface", ANY, "ip", "address", ANY, ANY)
    def normalize_vlan_ip(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_unit_inet_address(
            interface=if_name, unit=if_name, address=self.to_prefix(tokens[4], tokens[5])
        )

    @match("ip", "route-static", ANY, ANY, ANY)
    def normalize_default_gateway(self, tokens):
        yield self.make_inet_static_route_next_hop(
            route=self.to_prefix(tokens[2], tokens[3]), next_hop=tokens[4]
        )
