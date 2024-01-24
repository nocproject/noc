# ----------------------------------------------------------------------
# DLink.DxS config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST
from noc.core.confdb.syntax.patterns import IP_ADDRESS, INTEGER
from noc.core.validators import is_int


def iter_ports(first, last):
    first = first.replace("/", ":")
    last = last.replace("/", ":")

    slot_num = None
    if not is_int(first):
        slot_num = first.split(":")[0]

    if slot_num:
        first = first.replace(f"{slot_num}:", "")
        last = last.replace(f"{slot_num}:", "")

    first = int(first)
    last = int(last)

    for port_num in range(first, last+1):
        if slot_num:
            yield "%s:%s" % (slot_num, port_num)
        else:
            yield "%s" % port_num


class DLinkDxSNormalizer(BaseNormalizer):
    @match("config", "command_prompt", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[2].strip('"'))


    @match("config", "ports", REST)
    def normalize_interface(self, tokens):

        print(f"tokens {tokens}")
        if "-" in tokens[2]:
            port_range = tokens[2].split("-")
        else:
            port_range = (tokens[2], tokens[2])

        for port_num in iter_ports(port_range[0], port_range[1]):
            if_name = self.interface_name(port_num)
            print(f"ifname {if_name}")
            print(self.make_interface(interface=if_name))
            yield self.make_interface(interface=if_name)

#        if_name = self.interface_name(tokens[1], tokens[2])
#        yield self.make_interface(interface=if_name)


#    @match("username", ANY, "password", "encrypted", ANY, "privilege", ANY)
#    def normalize_username_access_level(self, tokens):
#        yield self.make_user_encrypted_password(username=tokens[1], password=" ".join(tokens[4]))
#        yield self.make_user_class(username=tokens[1], class_name="level-%s" % tokens[6])

#    @match("no", "spanning-tree")
#    def normalize_no_spanning_tree(self, tokens):
#        self.set_context("spanning_tree_disabled", True)
#        yield self.make_global_spanning_tree_status(status=False)

#    @match("interface", "gigabitethernet", ANY)
#    @match("interface", "vlan", ANY)
#    def normalize_interface(self, tokens):
#        if_name = self.interface_name(tokens[1], tokens[2])
#        yield self.make_interface(interface=if_name)

#    @match("interface", "gigabitethernet", ANY, "no", "shutdown")
#    @match("interface", "vlan", ANY, "no", "shutdown")
#    def normalize_interface_shutdown(self, tokens):
#        yield self.make_interface_admin_status(
#            interface=self.interface_name(tokens[1], tokens[2]), admin_status="on"
#        )

#    @match("interface", "gigabitethernet", ANY, "description", REST)
#    @match("interface", "vlan", ANY, "description", REST)
#    def normalize_interface_description(self, tokens):
#        yield self.make_interface_description(
#            interface=self.interface_name(tokens[1], tokens[2]), description=" ".join(tokens[4:])
#        )

#    @match(
#        "interface", "gigabitethernet", ANY, "storm-control", "broadcast", "level", "kbps", INTEGER
#    )
#    def normalize_port_storm_control_broadcast(self, tokens):
#        yield self.make_interface_storm_control_broadcast_level(
#            interface=self.interface_name(tokens[1], tokens[2]), level=tokens[-1]
#        )

#    @match(
#        "interface", "gigabitethernet", ANY, "storm-control", "multicast", "level", "kbps", INTEGER
#    )
#    def normalize_port_storm_control_multicast(self, tokens):
#        yield self.make_interface_storm_control_multicast_level(
#            interface=self.interface_name(tokens[1], tokens[2]), level=tokens[-1]
#        )

#    @match("interface", "gigabitethernet", ANY, "loopback-detection", "enable")
#    def normalize_interface_no_loop_detect(self, tokens):
#        if not self.get_context("loop_detect_disabled"):
#            if_name = self.interface_name(tokens[1], tokens[2])
#            yield self.make_loop_detect_interface(interface=if_name)

#    @match("interface", "vlan", ANY, "ip", "address", ANY, ANY)
#    def normalize_vlan_ip(self, tokens):
#        if_name = self.interface_name(tokens[1], tokens[2])
#        yield self.make_unit_inet_address(
#            interface=if_name, unit=if_name, address=self.to_prefix(tokens[-2], tokens[-1])
#        )

#    @match("ip", "route", "0.0.0.0", "0.0.0.0", IP_ADDRESS)
#    def normalize_default_gateway(self, tokens):
#        yield self.make_inet_static_route_next_hop(route="0.0.0.0/0", next_hop=tokens[-1])

#    @match("clock", "time", "source", ANY)
#    def normalize_timesource(self, tokens):
#        clock_source = "ntp" if tokens[-1] == "sntp" else tokens[-1]
#        yield self.make_clock_source(source=clock_source)

#    @match("sntp", "set", "sntp", "unicast-server", "ipv4", IP_ADDRESS)
#    def normalize_ntp_server(self, tokens):
#        yield self.make_ntp_server_address(name=tokens[-1], address=tokens[-1])
