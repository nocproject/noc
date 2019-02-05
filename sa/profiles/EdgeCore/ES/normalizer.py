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
