# ----------------------------------------------------------------------
# Eltex.MES config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY
from noc.core.confdb.syntax.patterns import IP_ADDRESS, INTEGER


class RCIOSNormalizer(BaseNormalizer):
    @match("hostname", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[1])

    @match("user", ANY, ANY, "local", "secret", ANY, "authorized-table", ANY, ANY)
    def normalize_username_access_level(self, tokens):
        yield self.make_user_encrypted_password(username=tokens[2], password=" ".join(tokens[5]))
        yield self.make_user_class(username=tokens[2])

    @match("interface", ANY)
    def normalize_interface(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_interface(interface=if_name)

    @match("interface", ANY, "aliasname", ANY)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(
            interface=self.interface_name(tokens[1]), description=tokens[3]
        )

    @match("interface", ANY, "switchport", "trunk", "permit", "vlan", ANY)
    def normalize_switchport_tagged(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_switchport_tagged(interface=if_name, unit=if_name, vlan_filter=tokens[-1])

    @match("interface", ANY, "ip", "address", ANY)
    def normalize_vlan_ip(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_unit_inet_address(interface=if_name, unit=if_name, address=tokens[4])

    @match("interface", ANY, "mtu", INTEGER)
    def normalize_interfce_mtu(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_interface_mtu(interface=if_name, mtu=tokens[3])

    @match("ip", "route", ANY, IP_ADDRESS)
    def normalize_default_gateway(self, tokens):
        yield self.make_inet_static_route_next_hop(route=tokens[2], next_hop=tokens[3])
