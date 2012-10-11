# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces, InterfaceTypeError
from noc.lib.ip import IPv4


def ranges_to_list_str(s):
    # Python modules:
    import re
    rx_range = re.compile(r"^(\d+)\s*-\s*(\d+)$")
    r = []
    for p in s.split(","):
        p = p.strip()
        try:
            int(p)
            r += [p]
            continue
        except:
            pass
        match = rx_range.match(p)
        if not match:
            raise SyntaxError
        f, t = [int(x) for x in match.groups()]
        if f >= t:
            raise SyntaxError
        for i in range(f, t + 1):
            r += [str(i)]
        #    return sorted(r)
    return (r)


class Script(NOCScript):
    name = "Alcatel.AOS.get_interfaces"
    implements = [IGetInterfaces]

    rx_line = re.compile(r"\w*Slot/Port", re.MULTILINE)
    rx_name = re.compile(r"\s+(?P<name>.\S+)\s+:", re.MULTILINE)
    rx_mac_local = re.compile(r"\s+MAC address\s+: (?P<mac>.+),",
        re.MULTILINE | re.IGNORECASE)
    rx_oper_status = re.compile(r"\s+Operational Status\s+: (?P<status>.+),",
        re.MULTILINE | re.IGNORECASE)
    rx_sh_svi = re.compile(
        r"(?P<name>\S+)\s+(?P<ip>\d+.\d+.\d+.\d+)\s+(?P<mask>\d+.\d+.\d+.\d+)"
        r"\s+UP\s+YES\s+vlan\s+(?P<vlan>\d+)", re.MULTILINE | re.IGNORECASE)

    types = {
        "e": "physical",  # FastEthernet
        "g": "physical",  # GigabitEthernet
        "t": "physical",  # TenGigabitEthernet
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
        r = []
        try:
            v = self.cli("show interfaces")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        switchports = {}  # interface -> (untagged, tagged)
        for swp in self.scripts.get_switchport():
            switchports[swp["interface"]] = (
            swp["untagged"] if "untagged" in swp else None,
            swp["tagged"]
            )

        v = "\n" + v
        # For each interface
        i = {
            "forwarding_instance": "default",
            "interfaces": [],
            "type": "physical"
        }
        for s in self.rx_line.split(v)[1:]:
            n = {}
            match = self.rx_name.search(s)
            if not match:
                continue
            n["name"] = match.group("name")
            iface = n["name"]
            match = self.rx_mac_local.search(s)
            if not match:
                continue
            n["mac"] = match.group("mac")
            match = self.rx_oper_status.search(s)
            if not match:
                continue
            n["oper_status"] = match.group("status")
            status = match.group("status").lower() == "up"
            n["admin_status"] = match.group("status")
            n["subinterfaces"] = [{
                "name": iface,
                "admin_status": True,
                "oper_status": True,
                "is_bridge": True,
                "enabled_afi": ["BRIDGE"],
                "mac": n["mac"],
                "description": ""
            }]
            if switchports[iface][1]:
                n["subinterfaces"][0]["tagged_vlans"] = switchports[iface][1]
            if switchports[iface][0]:
                n["subinterfaces"][0]["untagged_vlan"] = switchports[iface][0]
            n["type"] = "physical"
            r += [n]
        ip_int = self.cli("show ip interface")  # QWS-3xxx
        for match in self.rx_sh_svi.finditer(ip_int):
            ifname = match.group("name")
            ip = match.group("ip")
            enabled_afi = []
            if ":" in ip:
                ip_interfaces = "ipv6_addresses"
                ip_ver = "is_ipv6"
                enabled_afi += ["IPv6"]
                ip = IPv6(ip, netmask=match.group("mask")).prefix
                ip_list = [ip]
            else:
                ip_interfaces = "ipv4_addresses"
                ip_ver = "is_ipv4"
                enabled_afi += ["IPv4"]
                ip = IPv4(ip, netmask=match.group("mask")).prefix
                ip_list = [ip]
            vlan = match.group("vlan")
            a_stat = "UP"
            iface = {
                "name": ifname,
                "type": "SVI",
                "admin_status": True,
                "oper_status": True,
                "description": "",
                "subinterfaces": [{
                    "name": ifname,
                    "description": ifname,
                    "admin_status": True,
                    "oper_status": True,
                    ip_ver: True,
                    "enabled_afi": enabled_afi,
                    ip_interfaces: ip_list,
                    "vlan_ids": ranges_to_list_str(vlan),
                }]
            }
            r += [iface]
        return [{"interfaces": r}]
