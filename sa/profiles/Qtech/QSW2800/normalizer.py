# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Qtech.QSW2800 config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.normalizer.base import BaseNormalizer, match, ANY, REST
from noc.lib.text import ranges_to_list


class Qtech2800Normalizer(BaseNormalizer):
    @match("hostname", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[1])

    @match("no", "ip", "http", "server")
    def normalize_http_server(self, tokens):
        yield self.make_protocols_http()

    @match("username", ANY, "privilege", ANY)
    def normalize_username_access_level(self, tokens):
        yield self.make_user_class(
            username=tokens[1],
            class_name="level-%s" % tokens[3]
        )

    @match("username", ANY, "password", REST)
    def normalize_username_password(self, tokens):
        yield self.make_user_encrypted_password(
            username=tokens[1],
            password=" ".join(tokens[3:])
        )

    @match("snmp-server", "community", ANY, ANY, ANY)
    def normalize_snmp_community(self, tokens):
        yield self.make_snmp_community_level(
            community=tokens[4],
            level={"rw": "read-write", "ro": "read-only"}[tokens[2]]
        )

    @match("vlan", ANY, "name", ANY)
    def normalize_vlan_name(self, tokens):
        yield self.make_vlan_name(
            vlan_id=tokens[1],
            name=tokens[3]
        )

    @match("vlan", ANY)
    def normalize_vlan_id(self, tokens):
        for vlan in ranges_to_list(tokens[1], splitter=";"):
            yield self.make_vlan_id(vlan_id=vlan)

    @match("Interface", ANY)
    def normalize_interface(self, tokens):
        yield "interface", self.interface_name(tokens[1])

    @match("Interface", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(
            interface=self.interface_name(tokens[1]),
            description=" ".join(tokens[3:])
        )

    @match("Interface", ANY, "switchport", "security", "maximum", ANY)
    def normalize_port_security(self, tokens):
        yield self.make_unit_port_security_max_mac(
            interface=self.interface_name(tokens[1]),
            limit=tokens[5]
        )

    @match("Interface", ANY, "storm-control", "broadcast", ANY)
    def normalize_port_storm_control_broadcast(self, tokens):
        yield self.make_interface_storm_control_broadcast_level(
            interface=self.interface_name(tokens[1]),
            level=tokens[4]
        )

    @match("Interface", ANY, "storm-control", "multicast", ANY)
    def normalize_port_storm_control_multicast(self, tokens):
        yield self.make_interface_storm_control_multicast_level(
            interface=self.interface_name(tokens[1]),
            level=tokens[4]
        )

    @match("Interface", ANY, "storm-control", "unicast", ANY)
    def normalize_port_storm_control_unicast(self, tokens):
        yield self.make_interface_storm_control_unicast_level(
            interface=self.interface_name(tokens[1]),
            level=tokens[4]
        )

    @match("Interface", ANY, "switchport", "access", "vlan", ANY)
    def normalize_switchport_untagged(self, tokens):
        yield self.make_switchport_untagged(
            interface=self.interface_name(tokens[1]),
            vlan_filter=tokens[5]
        )

    @match("Interface", ANY, "switchport", "trunk", "allowed", "vlan", ANY)
    def normalize_switchport_tagged(self, tokens):
        yield self.make_switchport_tagged(
            interface=self.interface_name(tokens[1]),
            vlan_filter=ranges_to_list(tokens[7], splitter=";")
        )

    @match("Interface", ANY, "ip", "address", ANY, ANY)
    def normalize_vlan_ip(self, tokens):
        yield self.make_unit_inet_address(
            interface=self.interface_name(tokens[1]),
            address=self.to_prefix(tokens[4], tokens[5])
        )

    @match("ip", "default-gateway", ANY)
    def normalize_default_gateway(self, tokens):
        yield self.make_inet_static_route_next_hop(
            route="0.0.0.0/0",
            next_hop=tokens[2]
        )
