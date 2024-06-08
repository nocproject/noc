# ----------------------------------------------------------------------
# TPLink.T2600G config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST
from noc.core.confdb.syntax.patterns import IP_ADDRESS, INTEGER
from noc.core.text import ranges_to_list

tz_offset_match = re.compile(r"(?P<tz>\S+)(?P<offset>[+-]\d{2}:\d{2})")


class TPLinkT2600GNormalizer(BaseNormalizer):
    @match("user", "name", ANY, "privilege", ANY, "password", "7", ANY)
    def normalize_username_access_level(self, tokens):
        yield self.make_user_encrypted_password(username=tokens[2], password=" ".join(tokens[7:]))
        yield self.make_user_class(username=tokens[2], class_name="level-%s" % tokens[4])

    @match("hostname", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[1].strip('"'))

    @match("no", "spanning-tree")
    def normalize_no_spanning_tree(self, tokens):
        self.set_context("spanning_tree_disabled", True)
        yield self.make_global_spanning_tree_status(status=False)

    @match("spanning-tree")
    def normalize_spanning_tree(self, tokens):
        self.set_context("spanning_tree_disabled", False)
        yield self.make_global_spanning_tree_status(status=True)

    @match("spanning-tree", "mode", ANY)
    def normalize_spanning_tree_mode(self, tokens):
        yield self.make_spanning_tree_mode(mode=tokens[2])

    @match("vlan", ANY)
    def normalize_vlan(self, tokens):
        for vid in ranges_to_list(tokens[1]):
            yield self.make_vlan_id(vlan_id=vid)

    @match("vlan", ANY, "name", REST)
    def normalize_vlan_name(self, tokens):
        yield self.make_vlan_name(vlan_id=tokens[1], name=" ".join(tokens[3:]))

    @match("interface", "vlan", ANY)
    def normalize_interface_vlan(self, tokens):
        yield self.make_interface(interface="vlan")

    @match("interface", ANY, ANY)
    def normalize_interface_phys(self, tokens):
        if tokens[1] != "vlan":
            if_name = self.interface_name(tokens[1], tokens[2])
            yield self.make_interface(interface=if_name)

    @match("interface", ANY, ANY, "shutdown")
    def normalize_interface_shutdown(self, tokens):
        yield self.make_interface_admin_status(
            interface=self.interface_name(tokens[1], tokens[2]), admin_status="off"
        )

    @match("interface", ANY, ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(
            interface=self.interface_name(tokens[1], tokens[2]),
            description=" ".join(tokens[4:]).strip('"'),
        )

    @match("interface", "ten-gigabitEthernet", ANY, "storm-control", "broadcast", INTEGER)
    @match("interface", "gigabitEthernet", ANY, "storm-control", "broadcast", INTEGER)
    def normalize_port_storm_control_broadcast(self, tokens):
        yield self.make_interface_storm_control_broadcast_level(
            interface=self.interface_name(tokens[1], tokens[2]), level=tokens[-1]
        )

    @match("interface", "ten-gigabitEthernet", ANY, "storm-control", "multicast", INTEGER)
    @match("interface", "gigabitEthernet", ANY, "storm-control", "multicast", INTEGER)
    def normalize_port_storm_control_multicast(self, tokens):
        yield self.make_interface_storm_control_multicast_level(
            interface=self.interface_name(tokens[1], tokens[2]), level=tokens[-1]
        )

    @match("interface", "ten-gigabitEthernet", ANY, "loopback-detection")
    @match("interface", "gigabitEthernet", ANY, "loopback-detection")
    def normalize_interface_no_loop_detect(self, tokens):
        if not self.get_context("loop_detect_disabled"):
            if_name = self.interface_name(tokens[1], tokens[2])
            yield self.make_loop_detect_interface(interface=if_name)

    @match("interface", "vlan", ANY, "ip", "address", ANY, ANY)
    def normalize_vlan_ip(self, tokens):
        yield self.make_unit_inet_address(
            interface=tokens[1], unit=tokens[2], address=self.to_prefix(tokens[-2], tokens[-1])
        )

    @match("ip", "route", IP_ADDRESS, IP_ADDRESS, IP_ADDRESS)
    def normalize_ip_route(self, tokens):
        yield self.make_inet_static_route_next_hop(
            route=self.to_prefix(tokens[2], tokens[3]), next_hop=tokens[-1]
        )

    @match("system-time", "ntp", ANY, IP_ADDRESS, IP_ADDRESS, INTEGER)
    def normalize_tzoffset(self, tokens):
        v = tz_offset_match.match(tokens[2]).groupdict()
        tz_name = v.get("tz")
        tz_offset = v.get("offset")
        if tz_name is not None and tz_offset is not None:
            yield self.make_tz_offset(tz_name=tz_name, tz_offset=tz_offset)

        yield self.make_ntp_server_address(name=tokens[3], address=tokens[3])
        yield self.make_ntp_server_prefer(name=tokens[3])
        yield self.make_ntp_server_address(name=tokens[4], address=tokens[4])
