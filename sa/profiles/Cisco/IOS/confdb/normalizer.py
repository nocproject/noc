# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.IOS config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST, deferable


class CiscoIOSNormalizer(BaseNormalizer):
    @match("hostname", REST)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(" ".join(tokens[1:]))

    @match("no", "ip", "http", "server")
    def normalize_http_server(self, tokens):
        yield self.make_protocols_http()

    @match("no", "ip", "http", "secure-server")
    def normalize_https_server(self, tokens):
        yield self.make_protocols_https()

    @match("clock", "timezone", ANY, ANY)
    def normalize_timezone(self, tokens):
        yield self.make_tz_offset(tz_name=tokens[2], tz_offset=tokens[3])

    @match("snmp-server", "community", ANY, ANY, ANY)
    def normalize_snmp_protocol(self, tokens):
        yield self.make_snmp_community_level(
            community=tokens[2], level={"RO": "read-only", "RW": "read-write"}[tokens[3]]
        )

    @match("vlan", ANY)
    def normalize_vlan(self, tokens):
        yield self.make_vlan_id(vlan_id=tokens[1])

    @match("vlan", ANY, "name", REST)
    def normalize_vlan_name(self, tokens):
        yield self.make_vlan_name(vlan_id=tokens[1], name=" ".join(tokens[3:]))

    @match("interface", ANY)
    def normalize_interface_name(self, tokens):
        if "." in tokens[1]:
            pass
        #     ifname, unit = tokens[1].split(".")
        #     yield self.make_unit_description(
        #         interface=self.interface_name(ifname),
        #         unit=self.interface_name(tokens[1]),
        #         description="",
        #     )
        else:
            yield self.make_interface(interface=self.interface_name(tokens[1]))

    @match("interface", ANY, "shutdown")
    def normalize_interface_status(self, tokens):
        if "." not in tokens[1]:
            yield self.make_interface_admin_status(
                interface=self.interface_name(tokens[1]), admin_status=False
            )

    @match("interface", ANY, "mtu", ANY)
    def normalize_interface_mtu(self, tokens):
        yield self.make_interface_mtu(interface=self.interface_name(tokens[1]), mtu=tokens[3])

    @match("interface", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        if "." in tokens[1]:
            # ifname, unit = tokens[1].split(".")
            # yield self.make_unit_description(
            #     interface=self.interface_name(ifname),
            #     unit=self.interface_name(tokens[1]),
            #     description=" ".join(tokens[3:]),
            # )
            if_name = self.interface_name(tokens[1])
            yield self.defer(
                "fi.iface.%s" % if_name,
                self.make_unit_description,
                instance=deferable("instance"),
                interface=if_name,
                unit=self.interface_name(tokens[1]),
                description=" ".join(tokens[5:]),
            )
        else:
            yield self.make_interface_description(
                interface=self.interface_name(tokens[1]), description=" ".join(tokens[3:])
            )

    @match("interface", ANY, "speed", ANY)
    def normalize_interface_speed(self, tokens):
        if tokens[3] not in ["auto", "nonegotiate"]:
            yield self.make_interface_speed(
                interface=self.interface_name(tokens[1]), speed=tokens[3]
            )

    @match("interface", ANY, "duplex", ANY)
    def normalize_interface_duplex(self, tokens):
        yield self.make_interface_duplex(interface=self.interface_name(tokens[1]), duplex=tokens[3])

    @match("interface", ANY, "storm-control", "broadcast", "level", ANY)
    @match("interface", ANY, "storm-control", "broadcast", "level", ANY, ANY)
    @match("interface", ANY, "storm-control", "broadcast", "level", "bps", ANY, ANY)
    @match("interface", ANY, "storm-control", "broadcast", "level", "pps", ANY, ANY)
    def normalize_interface_storm_control_broadcast_pps(self, tokens):
        level = tokens[5]
        if tokens[5] in {"bps", "pps"}:
            level = tokens[6]
        yield self.make_interface_storm_control_broadcast_level(
            interface=self.interface_name(tokens[1]), level=level
        )

    @match("interface", ANY, "storm-control", "multicast", "level", ANY)
    @match("interface", ANY, "storm-control", "multicast", "level", ANY, ANY)
    @match("interface", ANY, "storm-control", "multicast", "level", "bps", ANY, ANY)
    @match("interface", ANY, "storm-control", "multicast", "level", "pps", ANY, ANY)
    def normalize_interface_storm_control_multicast_pps(self, tokens):
        level = tokens[5]
        if tokens[5] in {"bps", "pps"}:
            level = tokens[6]
        yield self.make_interface_storm_control_multicast_level(
            interface=self.interface_name(tokens[1]), level=level
        )

    @match("interface", ANY, "storm-control", "unicast", "level", ANY)
    @match("interface", ANY, "storm-control", "unicast", "level", ANY, ANY)
    @match("interface", ANY, "storm-control", "unicast", "level", "bps", ANY, ANY)
    @match("interface", ANY, "storm-control", "unicast", "level", "pps", ANY, ANY)
    def normalize_interface_storm_control_unicast_pps(self, tokens):
        level = tokens[5]
        if tokens[5] in {"bps", "pps"}:
            level = tokens[6]
        yield self.make_interface_storm_control_unicast_level(
            interface=self.interface_name(tokens[1]), level=level
        )

    @match("interface", ANY, "switchport", "access", "vlan", ANY)
    def normalize_switchport_untagged(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_switchport_untagged(interface=if_name, unit=if_name, vlan_filter=tokens[5])

    @match("interface", ANY, "switchport", "trunk", "allowed", "vlan", REST)
    def normalize_switchport_tagged(self, tokens):
        if_name = self.interface_name(tokens[1])
        vlan_filter = tokens[6]
        if tokens[6] == "add":
            vlan_filter = tokens[7]
        if tokens[6] != "none":
            yield self.make_switchport_tagged(
                interface=if_name, unit=if_name, vlan_filter=vlan_filter
            )

    @match("interface", ANY, "ip", "address", ANY, ANY)
    def normalize_interface_ip(self, tokens):
        # ifname = tokens[1]
        # if "." in ifname:
        #    ifname, unit = tokens[1].split(".")
        if_name = self.interface_name(tokens[1])
        yield self.defer(
            "fi.iface.%s" % if_name,
            self.make_unit_inet_address,
            instance=deferable("instance"),
            interface=if_name,
            unit=if_name,
            address=self.to_prefix(tokens[4], tokens[5]),
        )

        # yield self.make_unit_inet_address(
        #     interface=self.interface_name(ifname),
        #     unit=self.interface_name(tokens[1]),
        #     address=self.to_prefix(tokens[4], tokens[5]),
        # )

    @match("ip", "vrf", ANY)
    def normalize_routing_instances(self, tokens):
        yield self.make_forwarding_instance_type(instance=tokens[2], type="vrf")

    @match("ip", "vrf", ANY, "rd", ANY)
    def normalize_routing_instances_rd(self, tokens):
        yield self.make_forwarding_instance_rd(instance=tokens[2], rd=tokens[4])

    @match("ip", "vrf", ANY, "route-target", "export", ANY)
    def normalize_routing_instances_rt_export(self, tokens):
        yield self.make_forwarding_instance_export_target(instance=tokens[2], target=tokens[5])

    @match("ip", "vrf", ANY, "route-target", "import", ANY)
    def normalize_routing_instances_rt_import(self, tokens):
        yield self.make_forwarding_instance_import_target(instance=tokens[2], target=tokens[5])

    @match("ip", "vrf", ANY, "description", REST)
    def normalize_routing_instances_description(self, tokens):
        yield self.make_forwarding_instance_description(
            instance=tokens[2], description=" ".join(tokens[3:])
        )

    @match("spanning-tree", "mode", ANY)
    def normalize_spanning_tree_mode(self, tokens):
        yield self.make_spanning_tree_mode(mode=tokens[2])

    @match("interface", ANY, "spanning-tree", "portfast", ANY)
    def normalize_spanning_tree_interface_mode(self, tokens):
        yield self.make_spanning_tree_interface_mode(
            interface=self.interface_name(tokens[1]), mode="portfast"
        )

    @match("interface", ANY, "spanning-tree", "bpdufilter", "enable")
    def normalize_spanning_tree_bpdufilter(self, tokens):
        yield self.make_spanning_tree_interface_bpdu_filter(
            interface=self.interface_name(tokens[1]), enabled=True
        )

    @match("interface", ANY, "spanning-tree", "bpduguard", "enable")
    def normalize_spanning_tree_bpduguard(self, tokens):
        yield self.make_spanning_tree_interface_bpdu_guard(
            interface=self.interface_name(tokens[1]), enabled=True
        )

    @match("interface", ANY, "no", "cdp", "enable")
    def normalize_cdp_interface_disable(self, tokens):
        yield self.make_cdp_interface_disable(interface=self.interface_name(tokens[1]))

    @match("interface", ANY, "ip", "vrf", "forwarding", ANY)
    def normalize_interface_fi(self, tokens):
        yield self.defer("fi.iface.%s" % self.interface_name(tokens[1]), instance=tokens[5])

    @match("interface", ANY, "xconnect", ANY, ANY, "encapsulation", "mpls")
    def normalize_interface_xconnect(self, tokens):
        yield self.make_forwarding_instance_type(instance=tokens[4], type="vll")
        yield self.make_forwarding_instance_vpn_id(instance=tokens[4], vpn_id=tokens[4])
        # yield self.make_mpls_lsp_to_address(
        #     instance=tokens[4], address=tokens[3]
        # )
        yield self.defer("fi.iface.%s" % self.interface_name(tokens[1]), instance=tokens[4])
