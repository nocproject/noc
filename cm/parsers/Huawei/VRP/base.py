# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Basic Huawei parser
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
# Third-party modules
from pyparsing import nums, Word, Group, Optional, Suppress, Combine,\
    Literal, delimitedList
# NOC modules
from noc.lib.text import ranges_to_list
from noc.cm.parsers.base import BaseParser
from noc.core.ip import IPv4
from noc.lib.validators import is_ipv4, is_int


class BaseVRPParser(BaseParser):

    def __init__(self, managed_object):
        super(BaseVRPParser, self).__init__(managed_object)

    STATUSES = set(["sntp"])
    SERVICES = set(["telnet", "web", "ssh", "cluster",
                    "ntdp", "ndp", "lldp", "dhcp",
                    "http server", "http secure-server",
                    "telnet server", "stp", "info-center"])
    PROTOCOLS = set(["ntdp", "ndp", "bpdu"])

    def parse(self, config):
        # Various protocol statuses
        self.statuses = defaultdict(lambda: False)
        self.vlan_ids = {}  # name -> id
        self.undo = False # undo
        context = []
        inactive_level = 1

        for l in config.splitlines():
            if not l or l.startswith("#"):
                inactive_level = 1
                context = []
                continue
            ll = l.split()
            self.undo = False
            if l.startswith(" ", 0, 1):
                inactive_level = 2
                l = l.lstrip(" ")
            if l.startswith("  ", 0, 2):
                inactive_level = 3
                # context += ll[0]
                l = l.lstrip(" ")
            if l.startswith("undo"):
                self.undo = True
                ll = ll[1:]
                l = l.lstrip("undo ")
            if len(context) < inactive_level:
                context += [ll[0]]

            # Main block
            if l.startswith("sysname "):
                self.on_hostname(ll)
            elif l.startswith("!Software Version"):
                self.on_sw_version(ll)
            elif l.startswith("clock timezone"):
                self.on_timezone(ll)
            elif l.startswith("dns server"):
                self.on_system_name_server(ll)
            elif l.startswith("dns domain"):
                self.on_system_domain_name(ll)
            elif l.startswith("info-center loghost "):
                self.on_logging_host(ll)
            elif l.startswith("interface "):
                self.on_interface_context(ll)
                continue
            elif l.startswith("aaa"):
                continue
            elif "interface" in context:
                    if l.startswith("shutdown"):
                        self.on_interface_shutdown(ll)
                    elif l.startswith("description"):
                        self.on_interface_descripion(ll)
                    elif l.startswith("ip address "):
                        self.on_subinterface_ipv4_address(ll)
                    elif l.startswith("broadcast-suppression") or l.startswith("multicast-suppression") \
                            or l.startswith("unicast-suppression"):
                        self.on_storm_control(ll)
                    elif l.startswith("speed "):
                        self.on_interface_speed(ll)
                    elif l.startswith("duplex "):
                        self.on_interface_duplex(ll)
                    elif l.startswith("negotiation"):
                        # undo negotiation auto
                        pass
                    elif l.startswith("port link-type"):
                        # port link-type trunk
                        pass
                    elif l.startswith("port-security"):
                        self.on_interface_port_security(ll)
                    elif l.startswith("port trunk allow-pass ") or \
                            l.startswith("port hybrid tagged vlan "):
                        # port trunk allow-pass vlan 118 718
                        self.on_interface_tagged(ll)
                    elif l.startswith("port hybrid "):
                        # port hybrid pvid vlan 2925
                        # undo port hybrid vlan 1
                        # mac-limit maximum 6
                        self.on_interface_untagged(ll)
                    elif l.startswith("eth-trunk"):
                        self.on_interface_aggregate(ll)
                    elif ll[0] in self.PROTOCOLS:
                        self.on_interface_protocols(ll)
                    elif len(ll) > 1:
                        if ll[1] in self.PROTOCOLS:
                            self.on_interface_protocols(ll)
            elif l.startswith("vlan batch "):
                # vlan batch 777 1221 to 1244 2478 4010
                pass
            elif l.startswith("vlan "):
                self.on_vlan(ll)
            elif l.startswith("name ") and "vlan" in context:
                self.on_vlan_name(ll)
            elif l.startswith("description ") and "vlan" in context:
                self.on_vlan_name(ll)
            elif "aaa" in context:
                if l.startswith("local-user"):
                    self.on_system_login_user_class(ll)
            elif l.startswith("traffic-policy"):
                # traffic-policy
                pass
            elif l.startswith("snmp-agent sys-info location"):
                # snmp-agent sys-info location huawei_s23xx_a
                # snmp-agent sys-info contact config_v.028
                self.on_snmp_location(ll)
            elif l.startswith("ntp-service"):
                self.on_ntp_server(ll)
            elif len(ll) > 1 and ll[-1] in ("enable", "disable"):
                # if ll[0] in self.SERVICES:
                if " ".join(ll[:-1]) in self.SERVICES:
                    s = self.get_service_fact(" ".join(ll[:-1]))
                    s.enabled = not self.undo
            elif l.startswith("ip route-static"):
                self.on_ipv4_route(ll)
            # print context


        # Yield facts
        for f in self.iter_facts():
            yield f

    def get_interface_defaults(self, name):
        r = super(BaseVRPParser, self).get_interface_defaults(name)
        r["admin_status"] = True
        return r

    def get_subinterface_defaults(self):
        r = super(BaseVRPParser, self).get_subinterface_defaults()
        r["untagged_vlan"] = 1
        r["admin_status"] = True
        return r

    def get_user_defaults(self):
        return {
            "level": 0
        }

    def on_interface_context(self, tokens):
        # print tokens
        if tokens[1].startswith("Vlan"):
            si = self.get_subinterface_fact(tokens[1])
        else:
            iface = self.get_interface_fact(tokens[1])
            si = self.get_subinterface_fact(tokens[1])

    def on_interface_shutdown(self, tokens):
        status = self.undo
        si = self.get_current_subinterface()
        si.admin_status = status
        if "." not in si.name:
            si.interface.admin_status = status

    def on_interface_descripion(self, tokens):
        si = self.get_current_subinterface()
        description = " ".join(tokens[1:])
        if description.startswith("\"") and description.startswith("\""):
            description = description[1:-1]
        si.description = description
        if "." not in si.name:
            si.interface.description = description

    def on_interface_speed(self, tokens):
        """
        speed 10
        undo speed 10
        """
        if not self.undo:
            self.get_current_interface().speed = tokens[-1]

    def on_interface_duplex(self, tokens):
        """
        duplex 10
        """
        if not self.undo:
            self.get_current_interface().duplex = tokens[-1]

    def on_interface_speed_duplex(self, tokens):
        """

        """
        self.get_current_interface().speed = tokens[1].split("-")[0]
        self.get_current_interface().duplex = tokens[1].split("-")[1]

    def on_interface_aggregate(self, tokens):
        # eth-trunk 1
        self.get_current_interface().aggregated_interface = tokens[1]

    def on_interface_protocols(self, tokens):
        """
        ntdp enable
        ndp disable
        stp disable
        undo bpdu enable
        """
        if self.undo or tokens[-1] == "disable":
            self.get_current_interface().remove_protocol(tokens[0].upper())
        else:
            self.get_current_interface().add_protocol(tokens[0].upper())

    def on_hostname(self, tokens):
        """
        sysname S5300_D
        """
        self.get_system_fact().hostname = tokens[-1]

    def on_sw_version(self, tokens):
        """
        !Software Version V200R003C00SPC300
        """
        self.get_system_fact().version = tokens[-1]

    def on_timezone(self, tokens):
        """
        clock timezone MSK add 03:00:00
        """
        self.get_system_fact().timezone = tokens[2]

    def on_snmp_location(self, tokens):
        # snmp-agent sys-info location huawei_s23xx_a
        self.get_system_fact().location = " ".join(tokens[3:])

    def on_system_login_user_class(self, tokens):
        if not self.undo:	
            self.get_user_fact(tokens[1])
            if "privilege" == tokens[2]:
                self.get_user_fact(tokens[1]).level = tokens[4]

    def on_logging_host(self, tokens):
        """
        info-center loghost 10.46.147.5 channel 9
        """
        if len(tokens) > 2:
            self.get_sysloghost_fact(tokens[2])

    def on_ntp_server(self, tokens):
        """
        ntp-service unicast-server 1.1.1.1
        """
        if len(tokens) > 2:
            self.get_ntpserver_fact(tokens[2])

    def on_system_domain_name(self, tokens):
        """
        dns domain tversvyaz.net
        """
        self.get_system_fact().domain_name = tokens[-1]

    def on_system_name_server(self, tokens):
        """
        dns server 10.10.10.10
        """
        self.get_system_fact().nameservers += [tokens[-1]]

    def on_vlan(self, tokens):
        self.get_vlan_fact(int(tokens[-1].strip()))

    def on_vlan_name(self, tokens):
        self.get_current_vlan().name = tokens[-1]

    def on_storm_control(self, tokens):
        """
        multicast-suppression 1
        broadcast-suppression 1
        """
        si = self.get_current_subinterface()
        if tokens[0] == "broadcast-suppression":
            si.traffic_control_broadcast = True
        if tokens[0] == "multicast-suppression":
            si.traffic_control_multicast = True
        if tokens[0] == "unicast-suppression":
            si.traffic_control_unicast = True

    def on_interface_port_security(self, tokens):
        """
        port-security enable
        port-security max-mac-num 6
        """
        si = self.get_current_subinterface()
        if tokens[1] == "enable":
            si.port_security = True
        if tokens[1] == "max-mac-num":
                si.port_security_max = tokens[-1]

    def on_interface_untagged(self, tokens):
        """
        port hybrid pvid vlan 2925
        undo port hybrid vlan 1
        port hybrid untagged vlan 1223 2478
        port hybrid vlan 1757 untagged
        port hybrid vlan 1757 tagged
        """
        si = self.get_current_subinterface()

        if self.undo:
            if si.untagged_vlan == int(tokens[-1]):
                si.untagged_vlan = None
        else:
            if tokens[-1] == "untagged":
                si.untagged_vlan = int(tokens[-2])
            elif tokens[-1] == "tagged":
                si.tagged_vlans += [int(tokens[-2])]
            else:
                si.untagged_vlan = int(tokens[4])
            si.add_afi("BRIDGE")

    def on_interface_tagged(self, tokens):
        """
        undo port trunk allow-pass vlan 1
        port trunk allow-pass vlan 118 718
        port trunk allow-pass vlan 2 to 4094
        port trunk allow-pass vlan 76 90 118 123 126 165 to 169 175 to 179 621 2852 to 2854
        port hybrid tagged vlan 51 90 to 91 110 118 319 333 402 419 433 524 to 527
        """
        si = self.get_current_subinterface()
        vlans = " ".join(tokens[4:])
        if vlans != "none":
            for v in ranges_to_list(vlans, splitter=" "):
                si.tagged_vlans += [int(v)]
        si.add_afi("BRIDGE")

    def on_subinterface_ipv4_address(self, tokens):
        """
        ip address 10.10.10.10 255.255.254.0
        """
        si = self.get_current_subinterface()
        si.ipv4_addresses += [tokens[2]]
        si.add_afi("IPv4")

    def on_ipv4_route(self, tokens):
        """
        ip route-static 0.0.0.0 0.0.0.0 172.20.66.30 preference 30
        @todo ip route-static 10.10.10.0 255.255.254.0 Vlanif7 10.10.100.1
        """
        p = IPv4(tokens[2], netmask=tokens[3])
        sf = self.get_static_route_fact(str(p))
        # rest = tokens[3].split()
        # nh = rest.pop(0)
        nh = tokens[4]
        if is_ipv4(nh):
            sf.next_hop = nh
        else:
            pass
