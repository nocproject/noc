# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# MikroTik.RouterOS config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, deferable
from noc.core.confdb.syntax import INTEGER, IPv4_PREFIX, IPv4_ADDRESS


class RouterOSNormalizer(BaseNormalizer):
    @match("/system", "identity", "name", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[3])

    @match("/system", "clock", "time-zone-name", ANY)
    def normalize_time_zone_name(self, tokens):
        yield self.make_tz(tz_name=tokens[3])

    @match("/ip", "route", INTEGER, "dst-address", IPv4_PREFIX)
    def normalize_route_dst_address(self, tokens):
        yield self.defer("ip.route.%s" % tokens[2], route=tokens[4])

    @match("/ip", "route", INTEGER, "gateway", IPv4_ADDRESS)
    def normalize_route_gateway(self, tokens):
        yield self.defer(
            "ip.route.%s" % tokens[2],
            self.make_inet_static_route_next_hop,
            route=deferable("route"),
            next_hop=tokens[4],
        )

    @match("/ip", "route", INTEGER, "type", "blackhole")
    def normalize_route_type_blackhole(self, tokens):
        yield self.defer(
            "ip.route.%s" % tokens[2], self.make_inet_static_route_discard, route=deferable("route")
        )

    @match("/ip", "address", INTEGER, "address", IPv4_PREFIX)
    def normalize_interface_address(self, tokens):
        yield self.defer(
            "ip.address.%s" % tokens[2],
            self.make_unit_inet_address,
            interface=deferable("interface"),
            address=tokens[4],
        )

    @match("/ip", "address", INTEGER, "interface", ANY)
    def normalize_interface_address_interface(self, tokens):
        yield self.defer("ip.address.%s" % tokens[2], interface=tokens[4])
