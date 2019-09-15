# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# EdgeCore.ES config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST
from noc.core.text import ranges_to_list


class ESNormalizer(BaseNormalizer):
    @match("hostname", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[1])

    @match("prompt", ANY)
    def normalize_prompt(self, tokens):
        yield self.make_prompt(tokens[1])

    @match("username", ANY, "access-level", ANY)
    def normalize_username_access_level(self, tokens):
        yield self.make_user_class(username=tokens[1], class_name="level-%s" % tokens[3])

    @match("username", ANY, "password", REST)
    def normalize_username_password(self, tokens):
        yield self.make_user_encrypted_password(username=tokens[1], password=" ".join(tokens[3:]))

    @match("interface", "ethernet", ANY)
    def normalize_interface(self, tokens):
        if_name = self.interface_name(tokens[1], tokens[2])
        yield self.make_interface(interface=if_name)

    @match("interface", "ethernet", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(
            interface=self.interface_name(tokens[1], tokens[2]), description=" ".join(tokens[4:])
        )

    @match("interface", "ethernet", ANY, "shutdown")
    def normalize_interface_shutdown(self, tokens):
        yield self.make_interface_admin_status(
            interface=self.interface_name(tokens[1], tokens[2]), admin_status="off"
        )

    @match("interface", "ethernet", ANY, "port", "security", "max-mac-count", ANY)
    def normalize_port_security(self, tokens):
        if_name = self.interface_name(tokens[1], tokens[2])
        yield self.make_unit_port_security_max_mac(interface=if_name, unit=if_name, limit=tokens[6])

    @match("interface", "ethernet", ANY, "spanning-tree", "cost", ANY)
    def normalize_stp_cost(self, tokens):
        yield self.make_spanning_tree_interface_cost(
            interface=self.interface_name(tokens[1], tokens[2]), cost=tokens[5]
        )

    @match("interface", "ethernet", ANY, "switchport", "allowed", "vlan", "add", ANY, "untagged")
    def normalize_switchport_untagged(self, tokens):
        if_name = self.interface_name(tokens[1], tokens[2])
        yield self.make_switchport_untagged(interface=if_name, unit=if_name, vlan_filter=tokens[7])

    @match("interface", "ethernet", ANY, "switchport", "allowed", "vlan", "add", ANY, "tagged")
    def normalize_switchport_tagged(self, tokens):
        if_name = self.interface_name(tokens[1], tokens[2])
        yield self.make_switchport_tagged(interface=if_name, unit=if_name, vlan_filter=tokens[7])

    @match("interface", "ethernet", ANY, "switchport", "native", "vlan", ANY)
    def normalize_switchport_native(self, tokens):
        if_name = self.interface_name(tokens[1], tokens[2])
        yield self.make_switchport_native(interface=if_name, unit=if_name, vlan_id=tokens[6])

    @match("interface", "ethernet", ANY, "lldp", "admin-status", ANY)
    def normalize_interface_lldp_admin_status(self, tokens):
        if not self.get_context("lldp_disabled"):
            if_name = self.interface_name(tokens[1], tokens[2])
            status = tokens[5].lower()
            if status == "rx-only":
                yield self.make_lldp_admin_status_rx(interface=if_name)
            elif status == "tx-only":
                yield self.make_lldp_admin_status_tx(interface=if_name)
            elif status == "tx-rx":
                yield self.make_lldp_admin_status_rx(interface=if_name)
                yield self.make_lldp_admin_status_tx(interface=if_name)

    @match("interface", "ethernet", ANY, "no", "lldp", "admin-status")
    def normalize_interface_no_lldp_admin_status(self, tokens):
        if not self.get_context("lldp_disabled"):
            if_name = self.interface_name(tokens[1], tokens[2])
            yield self.make_lldp_interface_disable(interface=if_name)

    @match("interface", "ethernet", ANY, "no", "loopback-detection")
    def normalize_interface_no_loop_detect(self, tokens):
        if not self.get_context("loop_detect_disabled"):
            if_name = self.interface_name(tokens[1], tokens[2])
            yield self.make_loop_detect_interface_disable(interface=if_name)

    # @match("vlan", "database", "vlan", ANY, "name", ANY, "media", "ethernet", "state", "active")
    @match("vlan", "database", "vlan", ANY, "name", ANY, "media", "ethernet")
    @match("vlan", "database", "VLAN", ANY, "name", ANY, "media", "ethernet")
    def normalize_vlan_name(self, tokens):
        yield self.make_vlan_name(vlan_id=tokens[3], name=tokens[5])

    # @match("vlan", "database", "vlan", ANY, "media", "ethernet", "state", "active")
    @match("vlan", "database", "vlan", ANY, "media", "ethernet")
    @match("vlan", "database", "VLAN", ANY, "media", "ethernet")
    def normalize_vlan_id(self, tokens):
        for vlan_id in ranges_to_list(tokens[3]):
            yield self.make_vlan_id(vlan_id=str(vlan_id))

    @match("interface", "vlan", ANY, "ip", "address", ANY, ANY)
    def normalize_vlan_ip(self, tokens):
        if_name = self.interface_name(tokens[1], tokens[2])
        yield self.make_unit_inet_address(
            interface=if_name, unit=if_name, address=self.to_prefix(tokens[5], tokens[6])
        )

    @match("ip", "default-gateway", ANY)
    def normalize_default_gateway(self, tokens):
        yield self.make_inet_static_route_next_hop(route="0.0.0.0/0", next_hop=tokens[2])

    @match("spanning-tree")
    def normalize_spanning_tree(self, tokens):
        self.set_context("spanning_tree_disabled", False)
        yield self.make_global_spanning_tree_status(status=True)

    @match("spanning-tree", "priority", ANY)
    def normalize_spanning_tree_priority(self, tokens):
        yield self.make_spanning_tree_priority(priority=tokens[2])

    @match("no", "spanning-tree")
    def normalize_no_spanning_tree(self, tokens):
        self.set_context("spanning_tree_disabled", True)
        yield self.make_global_spanning_tree_status(status=False)

    @match("interface", "ethernet", ANY, "spanning-tree", "spanning-disabled")
    def normalize_no_interface_spanning_tree(self, tokens):
        if not self.get_context("spanning_tree_disabled"):
            if_name = self.interface_name(tokens[1], tokens[2])
            yield self.make_spanning_tree_interface_disable(interface=if_name)

    @match("no", "lldp")
    def normalize_no_lldp(self, tokens):
        self.set_context("lldp_disabled", True)
        yield self.make_global_lldp_status(status=False)

    @match("no", "loopback-detection")
    def normalize_no_loopback_detection(self, tokens):
        self.set_context("loop_detect_disabled", True)
        yield self.make_global_loop_detect_status(status=False)

    @match("ntp", "client")
    def normalize_timesource(self, tokens):
        yield self.make_clock_source(source="ntp")

    @match("ntp", "server", ANY)
    def normalize_ntp_server(self, tokens):
        yield self.make_ntp_server_address(name=tokens[2], address=tokens[2])
