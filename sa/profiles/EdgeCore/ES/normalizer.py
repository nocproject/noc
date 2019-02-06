# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# EdgeCore.ES config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.normalizer.base import BaseNormalizer, match, ANY, REST


class ESNormalizer(BaseNormalizer):
    @match("hostname", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[1])

    @match("prompt", ANY)
    def normalize_prompt(self, tokens):
        yield self.make_prompt(tokens[1])

    @match("username", ANY, "access-level", ANY)
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

    @match("interface", "ethernet", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(
            interface=self.interface_name(tokens[1], tokens[2]),
            description=" ".join(tokens[4:])
        )

    @match("interface", "ethernet", ANY, "port", "security", "max-mac-count", ANY)
    def normalize_port_security(self, tokens):
        yield self.make_unit_port_security_max_mac(
            interface=self.interface_name(tokens[1], tokens[2]),
            limit=tokens[6]
        )

    @match("interface", "ethernet", ANY, "spanning-tree", "cost", ANY)
    def normalize_stp_cost(self, tokens):
        yield self.make_spanning_tree_interface_cost(
            interface=self.interface_name(tokens[1], tokens[2]),
            cost=tokens[5]
        )

    @match("interface", "ethernet", ANY, "switchport", "allowed", "vlan", "add", ANY, "untagged")
    def normalize_switchport_untagged(self, tokens):
        yield self.make_switchport_untagged(
            interface=self.interface_name(tokens[1], tokens[2]),
            vlan_filter=tokens[7]
        )

    @match("interface", "ethernet", ANY, "switchport", "allowed", "vlan", "add", ANY, "tagged")
    def normalize_switchport_tagged(self, tokens):
        yield self.make_switchport_tagged(
            interface=self.interface_name(tokens[1], tokens[2]),
            vlan_filter=tokens[7]
        )

    @match("interface", "ethernet", ANY, "switchport", "native", "vlan", ANY)
    def normalize_switchport_tagged(self, tokens):
        yield self.make_switchport_native(
            interface=self.interface_name(tokens[1], tokens[2]),
            vlan_id=tokens[6]
        )

    @match("vlan", "database", "vlan", ANY, "name", ANY, "media", "ethernet", "state", "active")
    def normalize_vlan_name(self, tokens):
        yield self.make_vlan_name(
            vlan_id=tokens[3],
            name=tokens[5]
        )

    @match("vlan", "database", "vlan", ANY, "media", "ethernet", "state", "active")
    def normalize_vlan_id(self, tokens):
        yield self.make_vlan_id(vlan_id=tokens[3])

    @match("interface", "vlan", ANY, "ip", "address", ANY, ANY)
    def normalize_vlan_ip(self, tokens):
        yield self.make_unit_inet_address(
            interface=self.interface_name(tokens[1], tokens[2]),
            address=self.to_prefix(tokens[5], tokens[6])
        )

    @match("ip", "default-gateway", ANY)
    def normalize_default_gateway(self, tokens):
        yield self.make_inet_static_route_next_hop(
            route="0.0.0.0/0",
            next_hop=tokens[2]
        )
