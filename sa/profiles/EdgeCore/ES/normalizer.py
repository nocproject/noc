# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# EdgeCore.ES config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.normalizer.base import BaseNormalizer, match, ANY


class ESNormalizer(BaseNormalizer):
    @match("hostname", ANY)
    def normalize_hostname(self, tokens):
        yield "system", "hostname", tokens[1]

    @match("interface", "ethernet", ANY, "description", ANY)
    def normalize_interface_description(self, tokens):
        yield self.vr(
            "interface", self.interface_name(tokens[1], tokens[2]),
            "description", tokens[4]
        )

    @match("interface", "ethernet", ANY, "port", "security", "max-mac-count", ANY)
    def normalize_port_security(self, tokens):
        yield self.vr(
            "interface", self.interface_name(tokens[1], tokens[2]),
            "unit", "0", "bridge", "port-security", "max-mac-count", tokens[6]
        )

    @match("interface", "ethernet", ANY, "spanning-tree", "cost", ANY)
    def normalize_stp_cost(self, tokens):
        yield self.vr(
            "protocols", "spanning-tree",
            "interface", self.interface_name(tokens[1], tokens[2]),
            "cost", tokens[5]
        )

    @match("interface", "vlan", ANY, "ip", "address", ANY, ANY)
    def normalize_vlan_ip(self, tokens):
        yield self.vr(
            "interface", self.interface_name(tokens[1], tokens[2]),
            "unit", "0", "inet", "address", [self.to_prefix(tokens[5], tokens[6])]
        )

    @match("ip", "default-gateway", ANY)
    def normalize_default_gateway(self, tokens):
        yield self.vr(
            "route", "inet", "static", "0.0.0.0/0", "next-hop", tokens[2]
        )
