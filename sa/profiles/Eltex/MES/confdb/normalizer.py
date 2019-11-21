# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Eltex.MES config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST
from noc.core.text import ranges_to_list


class MESNormalizer(BaseNormalizer):
    @match("hostname", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[1])

    @match("no", "ip", "http", "server")
    def normalize_http_server(self, tokens):
        yield self.make_protocols_http()

    @match("ip", "ssh", "server")
    def normalize_ssh_server(self, tokens):
        yield self.make_protocols_ssh()

    @match("username", ANY, "password", "encrypted", ANY, "privilege", ANY)
    def normalize_username_access_level(self, tokens):
        yield self.make_user_encrypted_password(username=tokens[1], password=" ".join(tokens[4]))
        yield self.make_user_class(username=tokens[1], class_name="level-%s" % tokens[6])

    @match("vlan", "database", "vlan", REST)
    def normalize_vlan_id_batch(self, tokens):
        for vlan in ranges_to_list(tokens[3]):
            yield self.make_vlan_id(vlan_id=vlan)

    @match("no", "spanning-tree")
    def normalize_no_spanning_tree(self, tokens):
        self.set_context("spanning_tree_disabled", True)
        yield self.make_global_spanning_tree_status(status=False)

    @match("interface", ANY)
    def normalize_interface(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_interface(interface=if_name)

    @match("interface", ANY, "shutdown")
    def normalize_interface_shutdown(self, tokens):
        yield self.make_interface_admin_status(
            interface=self.interface_name(tokens[1], tokens[2]), admin_status="off"
        )

    @match("interface", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(
            interface=self.interface_name(tokens[1]), description=" ".join(tokens[2:])
        )

    @match("interface", ANY, "port", "security", "max", ANY)
    def normalize_port_security_max_mac(self, tokens):
        yield self.make_unit_port_security_max_mac(
            interface=self.interface_name(tokens[1]), limit=tokens[5]
        )

    @match("interface", ANY, "broadcast", "level", "kpbs", ANY)
    def normalize_port_storm_control_broadcast(self, tokens):
        yield self.make_interface_storm_control_broadcast_level(
            interface=self.interface_name(tokens[1]), level=tokens[5]
        )

    @match("interface", ANY, "multicast", "level", "kpbs", ANY)
    def normalize_port_storm_control_multicast(self, tokens):
        yield self.make_interface_storm_control_multicast_level(
            interface=self.interface_name(tokens[1]), level=tokens[5]
        )

    @match("interface", ANY, "unknown-unicast", "level", "kpbs", ANY)
    def normalize_port_storm_control_unicast(self, tokens):
        yield self.make_interface_storm_control_unicast_level(
            interface=self.interface_name(tokens[1]), level=tokens[5]
        )

    @match("interface", ANY, "loopback-detection", "enable")
    def normalize_interface_no_loop_detect(self, tokens):
        if not self.get_context("loop_detect_disabled"):
            if_name = self.interface_name(tokens[1])
            yield self.make_loop_detect_interface(interface=if_name)

    @match("interface", ANY, "spanning-tree", "disable")
    def normalize_no_interface_spanning_tree(self, tokens):
        if not self.get_context("spanning_tree_disabled"):
            if_name = self.interface_name(tokens[1])
            yield self.make_spanning_tree_interface_disable(interface=if_name)

    @match("interface", ANY, "spanning-tree", "bpdu", "filtering")
    def normalize_interface_stp_bpdu_filter(self, tokens):
        yield self.make_spanning_tree_interface_bpdu_filter(
            interface=self.interface_name(tokens[1]), enabled=True
        )

    @match("interface", ANY, "no", "lldp", ANY)
    def normalize_interface_lldp_admin_status(self, tokens):
        if not self.get_context("lldp_disabled"):
            if_name = self.interface_name(tokens[1])
            status = tokens[4].lower()
            if status == "receive":
                yield self.make_lldp_admin_status_rx(interface=if_name)
            elif status == "transmit":
                yield self.make_lldp_admin_status_tx(interface=if_name)

    @match("interface", ANY, "switchport", ANY, "allowed", "vlan", "add", ANY, "tagged")
    @match("interface", ANY, "switchport", ANY, "allowed", "vlan", "add", ANY)
    def normalize_switchport_tagged(self, tokens):
        if_name = self.interface_name(tokens[1])
        for vlan in ranges_to_list(tokens[7]):
            yield self.make_switchport_tagged(interface=if_name, unit=if_name, vlan_filter=vlan)

    @match("interface", ANY, "switchport", ANY, "allowed", "vlan", "add", ANY, "untagged")
    def normalize_switchport_untagged(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_switchport_untagged(interface=if_name, unit=if_name, vlan_filter=tokens[7])

    @match("interface", ANY, "switchport", ANY, "native", "vlan", ANY)
    def normalize_switchport_native(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_switchport_native(interface=if_name, unit=if_name, vlan_id=tokens[6])

    @match("interface", ANY, "switchport", ANY, "pvid", ANY)
    def normalize_switchport_pvid(self, tokens):
        if_name = self.interface_name(tokens[1])
        if tokens[3] == "general":
            yield self.make_switchport_native(interface=if_name, unit=if_name, vlan_id=tokens[5])
        else:
            yield self.make_switchport_untagged(
                interface=if_name, unit=if_name, vlan_filter=tokens[5]
            )

    # @match("ip", "igmp", "vlan", ANY)
    # def normalize_igmp_snoopiing_vlan(self, tokens):
    #     yield self.

    @match("interface", ANY, "ip", "address", ANY, ANY)
    def normalize_vlan_ip(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_unit_inet_address(
            interface=if_name, unit=if_name, address=self.to_prefix(tokens[4], tokens[5])
        )

    @match("ip", "default-gateway", ANY)
    def normalize_default_gateway(self, tokens):
        yield self.make_inet_static_route_next_hop(route="0.0.0.0/0", next_hop=tokens[2])

    # selective-qinq list ingress add_vlan 1000
    @match("interface", ANY, "selective-qinq", "list", "ingress", "add_vlan", ANY)
    def normalize_add_vlan(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_input_vlan_map_rewrite_vlan(
            interface=if_name,
            unit=if_name,
            num="1",
            # stack="1",
            # inner_vlans=tokens[8],
            op="push",
            vlan=tokens[6],
        )

    # selective-qinq list ingress permit ingress_vlan 100,101,102,103
    @match("interface", ANY, "selective-qinq", "list", "egress", "permit", "ingress_vlan", ANY)
    @match("interface", ANY, "selective-qinq", "list", "ingress", "permit", "ingress_vlan", ANY)
    def normalize_ingress_vlan(self, tokens):
        if_name = self.interface_name(tokens[1])
        if tokens[4] == "ingress":
            yield self.make_input_vlan_map_inner_vlans(
                interface=if_name, unit=if_name, num="1", vlan_filter=tokens[7]
            )
        else:
            yield self.make_output_vlan_map_outer_vlans(
                interface=if_name, unit=if_name, num="1", vlan_filter=tokens[7]
            )

    @match(
        "interface",
        ANY,
        "selective-qinq",
        "list",
        "egress",
        "override_vlan",
        ANY,
        "ingress_vlan",
        ANY,
    )
    @match(
        "interface",
        ANY,
        "selective-qinq",
        "list",
        "ingress",
        "override_vlan",
        ANY,
        "ingress_vlan",
        ANY,
    )
    def normalize_ingress_override_vlan(self, tokens):
        if_name = self.interface_name(tokens[1])
        if tokens[4] == "ingress":
            yield self.make_input_vlan_map_inner_vlans(
                interface=if_name, unit=if_name, num="1", vlan_filter=tokens[8]
            )
            yield self.make_input_vlan_map_rewrite_vlan(
                interface=if_name, unit=if_name, num="1", op="swap", vlan=tokens[6]
            )
        else:
            yield self.make_output_vlan_map_outer_vlans(
                interface=if_name, unit=if_name, num="1", vlan_filter=tokens[8]
            )
            yield self.make_output_vlan_map_rewrite_vlan(
                interface=if_name, unit=if_name, num="1", op="swap", vlan=tokens[6]
            )

    # selective-qinq list ingress add_vlan 1000 ingress_vlan 100,200
    @match(
        "interface", ANY, "selective-qinq", "list", "egress", "add_vlan", ANY, "ingress_vlan", ANY
    )
    @match(
        "interface", ANY, "selective-qinq", "list", "ingress", "add_vlan", ANY, "ingress_vlan", ANY
    )
    def normalize_ingress_add_vlan(self, tokens):
        if_name = self.interface_name(tokens[1])
        if tokens[4] == "ingress":
            yield self.make_input_vlan_map_inner_vlans(
                interface=if_name, unit=if_name, num="1", vlan_filter=tokens[8]
            )
            yield self.make_input_vlan_map_rewrite_vlan(
                interface=if_name, unit=if_name, num="1", op="push", vlan=tokens[6]
            )
        else:
            yield self.make_output_vlan_map_outer_vlans(
                interface=if_name, unit=if_name, num="1", vlan_filter=tokens[8]
            )
            yield self.make_output_vlan_map_rewrite_vlan(
                interface=if_name, unit=if_name, num="1", op="push", vlan=tokens[6]
            )

    @match("clock", "source", ANY)
    def normalize_timesource(self, tokens):
        if tokens[2] == "sntp":
            yield self.make_clock_source(source="ntp")

    @match("sntp", "server", ANY)
    @match("sntp", "server", ANY, ANY)
    @match("sntp", "server", ANY, ANY, ANY)
    @match("sntp", "server", ANY, ANY, ANY, ANY)
    def normalize_ntp_server(self, tokens):
        yield self.make_ntp_server_address(name=tokens[2], address=tokens[2])
