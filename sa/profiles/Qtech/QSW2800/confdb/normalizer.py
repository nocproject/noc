# ----------------------------------------------------------------------
# Qtech.QSW2800 config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST
from noc.core.text import ranges_to_list


class Qtech2800Normalizer(BaseNormalizer):
    @match("hostname", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[1])

    @match("no", "ip", "http", "server")
    def normalize_http_server(self, tokens):
        yield self.make_protocols_http()

    @match("username", ANY, "privilege", ANY)
    def normalize_username_access_level(self, tokens):
        yield self.make_user_class(username=tokens[1], class_name="level-%s" % tokens[3])

    @match("username", ANY, "password", REST)
    def normalize_username_password(self, tokens):
        yield self.make_user_encrypted_password(username=tokens[1], password=" ".join(tokens[3:]))

    @match("snmp-server", "community", ANY, ANY, ANY, "access", ANY)
    def normalize_snmp_community_with_acl(self, tokens):
        yield self.make_snmp_community_level(
            community=tokens[4].strip('"'), level={"rw": "read-write", "ro": "read-only"}[tokens[2]]
        )

    @match("snmp-server", "community", ANY, ANY)
    def normalize_snmp_community_simple(self, tokens):
        try:
            level = {"rw": "read-write", "ro": "read-only"}[tokens[3]]
        except KeyError:
            return
        yield self.make_snmp_community_level(community=tokens[2].strip('"'), level=level)

    @match("snmp-server", "community", ANY, ANY, "encrypted")
    def normalize_snmp_community(self, tokens):
        yield self.make_snmp_community_level(
            community=tokens[2].strip('"'), level={"rw": "read-write", "ro": "read-only"}[tokens[3]]
        )

    @match("vlan", ANY, "name", ANY)
    def normalize_vlan_name(self, tokens):
        yield self.make_vlan_name(vlan_id=tokens[1], name=tokens[3])

    @match("vlan", ANY)
    def normalize_vlan_id(self, tokens):
        if tokens[1] == "database":
            return
        splitter = ";"
        if "," in tokens[1]:
            splitter = ","
        for vlan in ranges_to_list(tokens[1], splitter=splitter):
            yield self.make_vlan_id(vlan_id=vlan)

    @match("interface", ANY)
    @match("Interface", ANY)
    def normalize_interface(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_interface(interface=if_name)

    @match("Interface", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(
            interface=self.interface_name(tokens[1]), description=" ".join(tokens[3:])
        )

    @match("Interface", ANY, "shutdown")
    def normalize_interface_shutdown(self, tokens):
        yield self.make_interface_admin_status(
            interface=self.interface_name(tokens[1]), admin_status=False
        )

    @match("lldp", "enable")
    def normalize_enable_lldp(self, tokens):
        self.set_context("lldp_disabled", False)
        yield self.make_global_lldp_status(status=True)

    # @match("enable", "stp")
    # def normalize_enable_stp(self, tokens):
    #     self.set_context("stp_disabled", False)
    #     yield self.make_global_stp_status(status=True)

    @match("Interface", ANY, "lldp", "disable")
    def normalize_interface_lldp_enable(self, tokens):
        yield self.make_lldp_interface_disable(interface=self.interface_name(tokens[1]))

    @match("Interface", ANY, "switchport", "security", "maximum", ANY)
    def normalize_port_security(self, tokens):
        yield self.make_unit_port_security_max_mac(
            interface=self.interface_name(tokens[1]), limit=tokens[5]
        )

    @match("Interface", ANY, "storm-control", "broadcast", ANY)
    def normalize_port_storm_control_broadcast(self, tokens):
        yield self.make_interface_storm_control_broadcast_level(
            interface=self.interface_name(tokens[1]), level=tokens[4]
        )

    @match("Interface", ANY, "storm-control", "multicast", ANY)
    def normalize_port_storm_control_multicast(self, tokens):
        yield self.make_interface_storm_control_multicast_level(
            interface=self.interface_name(tokens[1]), level=tokens[4]
        )

    @match("Interface", ANY, "storm-control", "unicast", ANY)
    def normalize_port_storm_control_unicast(self, tokens):
        yield self.make_interface_storm_control_unicast_level(
            interface=self.interface_name(tokens[1]), level=tokens[4]
        )

    @match("Interface", ANY, "switchport", "access", "vlan", ANY)
    def normalize_switchport_untagged(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_switchport_untagged(interface=if_name, unit=if_name, vlan_filter=tokens[5])

    @match("Interface", ANY, "switchport", "trunk", "allowed", "vlan", ANY)
    def normalize_switchport_tagged(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_switchport_tagged(
            interface=if_name,
            unit=if_name,
            vlan_filter=",".join(str(x) for x in ranges_to_list(tokens[6], splitter=";")),
        )

    @match("interface", ANY, "ip", "address", ANY, ANY)
    @match("Interface", ANY, "ip", "address", ANY, ANY)
    def normalize_vlan_ip(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_unit_inet_address(
            interface=if_name, unit=if_name, address=self.to_prefix(tokens[4], tokens[5])
        )

    @match("ip", "default-gateway", ANY)
    def normalize_default_gateway(self, tokens):
        yield self.make_inet_static_route_next_hop(route="0.0.0.0/0", next_hop=tokens[2])

    @match("ntp", "enable")
    @match("sntp", "polltime", ANY)
    def normalize_timesource(self, tokens):
        yield self.make_clock_source(source="ntp")

    @match("ntp", "server", ANY)
    @match("sntp", "server", ANY)
    @match("ntp", "server", ANY, ANY)
    @match("sntp", "server", ANY, ANY)
    @match("ntp", "server", ANY, ANY, ANY)
    @match("sntp", "server", ANY, ANY, ANY)
    def normalize_ntp_server(self, tokens):
        addr = tokens[2].strip('"')
        yield self.make_ntp_server_address(name=addr, address=addr)
