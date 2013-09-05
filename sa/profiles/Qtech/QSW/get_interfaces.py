# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
from __future__ import with_statement
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4
from noc.lib.ip import IPv6


class Script(NOCScript):
    """
    Qtech.QSW.get_interfaces
    @todo: VRF support
    @todo: IPv6
    @todo: ISIS
    @todo: isis, bgp, rip
    @todo: subinterfaces
    @todo: Q-in-Q
    """
    name = "Qtech.QSW.get_interfaces"
    implements = [IGetInterfaces]

    TIMEOUT = 600

    rx_mac = re.compile(r"^The mac-address of interface is\s+(?P<mac>\S+)$",
        re.MULTILINE)

    rx_sh_svi = re.compile(
        r"^(Interface description\s*:\s*(?P<description>(\S+ \S+ \S+|\S+ \S+|\S+)).|)Interface name\s*:\s*(?P<interface>\S+?).Primary ipaddress\s*:\s*(?P<ip1>\d+\.\d+\.\d+\.\d+)/(?P<mask1>\d+\.\d+\.\d+\.\d+).Secondary ipaddress\s*:\s*((?P<ip2>\d+\.\d+\.\d+\.\d+)/(?P<mask2>\d+\.\d+\.\d+\.\d+)|None).VLAN\s*:\s*(?P<vlan>\d+).Address-range\s*:\s*\S+.Interface status\s*:\s*(?P<admin_status>(Up|Down))",
        re.DOTALL|re.MULTILINE)

    rx_sh_mng = re.compile(
        r"^ip address\s*:\s*(?P<ip>\d+\.\d+\.\d+\.\d+).netmask\s*:\s*(?P<mask>\d+\.\d+\.\d+\.\d+).gateway\s*:\s*\S+.ManageVLAN\s*:\s*(?P<vlan>\S+).MAC address\s*:\s*(?P<mac>\S+)",
        re.DOTALL|re.MULTILINE)

    rx_status = re.compile(
        r"^\s*Ethernet\s+(?P<interface>\S+)\s+is\s+(?P<admin_status>(enabled|disabled)),\s+port+\s+link+\s+is\s+(?P<oper_status>(up|down))",
        re.MULTILINE)

    types = {
        "e": "physical",    # FastEthernet
        "g": "physical",    # GigabitEthernet
        "t": "physical",    # TenGigabitEthernet
        }

    def get_ospfint(self):
        ospfs = []
        return ospfs

    def get_ripint(self):
        rip = []
        return rip

    def get_bgpint(self):
        bgp = []
        return bgp

    def execute(self):

        # TODO
        # Get portchannes
        portchannel_members = {}  # member -> (portchannel, type)
#        with self.cached():
#            for pc in self.scripts.get_portchannel():
#                i = pc["interface"]
#                t = pc["type"] == "L"
#                for m in pc["members"]:
#                    portchannel_members[m] = (i, t)

        interfaces = []

        # Try SNMP first

        """
        # SNMP working but without IP
        
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get mac
                mac = self.scripts.get_chassis_id()
                # Get switchports
                for swp in self.scripts.get_switchport():
                    iface = swp["interface"]
                    if iface[0] == "T":
                        return 1
                    # IF-MIB::ifAdminStatus
                    if len(iface.split('/')) < 3:
                        if_OID = iface.split('/')[1]
                    else:
                        if_OID = iface.split('/')[2]
                    s = self.snmp.get("1.3.6.1.2.1.2.2.1.7.%d" % int(if_OID))
                    admin = int(s) == 1

                    name = swp["interface"]
                    iface = {
                        "name": name,
                        "type": "aggregated" if len(swp["members"]) > 0 else "physical",
                        "admin_status": admin,
                        "oper_status": swp["status"],
                        "mac": mac,
                        "subinterfaces": [{
                            "name": name,
                            "admin_status": admin,
                            "oper_status": swp["status"],
                            "is_bridge": True,
                            "mac": mac,
                            #"snmp_ifindex": self.scripts.get_ifindex(interface=name)
                        }]
                    }
                    if swp["tagged"]:
                        iface["subinterfaces"][0]["tagged_vlans"] = swp["tagged"]
                    try:
                        iface["subinterfaces"][0]["untagged_vlan"] = swp["untagged"]
                    except KeyError:
                        pass
                    if swp["description"]:
                        iface["description"] = swp["description"]
                    if name in portchannel_members:
                        iface["aggregated_interface"] = portchannel_members[name][0]
                        iface["is_lacp"] = portchannel_members[name][1]
                    interfaces += [iface]

                return [{"interfaces": interfaces}]

            except self.snmp.TimeOutError:
                pass  # Fallback to CLI
        """

        # Fallback to CLI
        # Get port-to-vlan mappings
        pvm = {}
        switchports = {}  # interface -> (untagged, tagged)
        for swp in self.scripts.get_switchport():
            switchports[swp["interface"]] = (
                    swp["untagged"] if "untagged" in swp else None,
                    swp["tagged"],
                    swp["description"]
                    )

        interfaces = []

        # Get L3 interfaces
        try:
            enabled_afi = []
            ip_int = self.cli("show ip interface")  # QWS-3xxx
            match = self.rx_mac.search(ip_int)
            mac = match.group("mac")

            # TODO Get router interfaces
            ospfs = self.get_ospfint()
            rips = self.get_ripint()
            bgps = self.get_bgpint()

            for match in self.rx_sh_svi.finditer(ip_int):
                description = match.group("description")
                if not description:
                    description = 'Outband managment'
                ifname = match.group("interface")
                ip1 = match.group("ip1")
                ip2 = match.group("ip2")
                if ":" in ip1:
                    ip_interfaces = "ipv6_addresses"
                    enabled_afi += ["IPv6"]
                    ip1 = IPv6(ip1, netmask=match.group("mask1")).prefix
                    if ip2:
                        ip2 = IPv6(ip2, netmask=match.group("mask2")).prefix
                        ip_list = [ip1, ip2]
                    else:
                        ip_list = [ip1]
                else:
                    ip_interfaces = "ipv4_addresses"
                    enabled_afi += ["IPv4"]
                    ip1 = IPv4(ip1, netmask=match.group("mask1")).prefix
                    if ip2:
                        ip2 = IPv4(ip2, netmask=match.group("mask2")).prefix
                        ip_list = [ip1, ip2]
                    else:
                        ip_list = [ip1]
                vlan = match.group("vlan")
                a_stat = match.group("admin_status").lower() == "up"
                iface = {
                    "name": ifname,
                    "type": "SVI",
                    "admin_status": a_stat,
                    "oper_status": a_stat,
                    "mac": mac,
                    "description": description,
                    "subinterfaces": [{
                                "name": ifname,
                                "description": description,
                                "admin_status": a_stat,
                                "oper_status": a_stat,
                                "enabled_afi": enabled_afi,
                                ip_interfaces: ip_list,
                                "mac": mac,
                                "vlan_ids": self.expand_rangelist(vlan),
                            }]
                    }
                interfaces += [iface]

        except self.CLISyntaxError:
            enabled_afi = []
            ip_int = self.cli("show ip")  # QWS-2xxx
            match = self.rx_sh_mng.search(ip_int)
            ip = match.group("ip")
            if ":" in ip:
                ip_interfaces = "ipv6_addresses"
                enabled_afi += ["IPv6"]
                ip = IPv6(ip, netmask=match.group("mask")).prefix
            else:
                ip_interfaces = "ipv4_addresses"
                enabled_afi += ["IPv4"]
                ip = IPv4(ip, netmask=match.group("mask")).prefix
            ip_list = [ip]
            vlan = match.group("vlan")
            mac = match.group("mac")

            iface = {
                "name": "VLAN-" + vlan,
                "type": "management",
                "admin_status": True,
                "oper_status": True,
                "mac": mac,
                "description": 'Managment',
                "subinterfaces": [{
                            "name": "VLAN-" + vlan,
                            "description": 'Managment',
                            "admin_status": True,
                            "oper_status": True,
                            "enabled_afi": enabled_afi,
                            ip_interfaces: ip_list,
                            "mac": mac,
                            "vlan_ids": self.expand_rangelist(vlan),
                        }]
                }
            interfaces += [iface]
        #

        # Get L2 interfaces
        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        status = self.cli("show interface")
        for match in self.rx_status.finditer(status):
            ifname = match.group("interface")
            a_stat = match.group("admin_status").lower() == "enabled"
            o_stat = match.group("oper_status").lower() == "up"

            iface = {
                "name": ifname,
                "type": self.types[ifname[:1]],
                "admin_status": a_stat,
                "oper_status": o_stat,
                "mac": mac,
                "description": switchports[ifname][2],
                "subinterfaces": [{
                            "name": ifname,
                            "description": switchports[ifname][2],
                            "admin_status": a_stat,
                            "oper_status": o_stat,
                            "enabled_afi": ["BRIDGE"],
                            "mac": mac,
                            #"snmp_ifindex": self.scripts.get_ifindex(interface=name)
                        }]
                }

            if switchports[ifname][1]:
                iface["subinterfaces"][0]["tagged_vlans"] = switchports[ifname][1]
            if switchports[ifname][0]:
                iface["subinterfaces"][0]["untagged_vlan"] = switchports[ifname][0]

#            iface["description"] = switchports[ifname][2]

            # Portchannel member
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] = ["LACP"]
            interfaces += [iface]

        return [{"interfaces": interfaces}]
