# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.ASA.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(BaseScript):
    name = "Cisco.ASA.get_interfaces"
    interface = IGetInterfaces

    rx_int = re.compile(r"(?P<interface>\S+)\s\"(?P<alias>[\w-]*)\"\,\sis(\sadministratively)?\s(?P<admin_status>up|down),\s+line\s+protocol\s+is\s+(?P<oper_status>up|down)", re.MULTILINE | re.IGNORECASE)
    rx_mac = re.compile(r"MAC\saddress\s(?P<mac>\w{4}\.\w{4}\.\w{4})",
        re.MULTILINE | re.IGNORECASE)
    rx_vlan = re.compile(r"VLAN\sIdentifier\s(?P<vlan>\w+)",
        re.MULTILINE | re.IGNORECASE)
    rx_ospf = re.compile(r"^(?P<name>\w+)\sis\sup|down\,",
        re.MULTILINE | re.IGNORECASE)
    rx_ip = re.compile(r"IP\saddress\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\, subnet mask (?P<mask>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", re.MULTILINE | re.IGNORECASE)

    def get_ospfint(self):
        v = self.cli("show ospf interface")
        ospfs = []
        for s in v.split("\n"):
            match = self.rx_ospf.search(s)
            if match:
                ospfs.append(match.group("name"))
        return ospfs

    def execute(self):
        interfaces = []
        ospfs = self.get_ospfint()
        types = {
            "L": "loopback",
            "E": "physical",
            "G": "physical",
            "T": "physical",
            "M": "management",
            "R": "aggregated",
            "P": "aggregated",
            "V": "SVI"
        }
        if self.capabilities.get("Cisco | ASA | Security | Context | Mode"):
            if self.capabilities["Cisco | ASA | Security | Context | Mode"] == "multiple":
                self.cli("changeto system")
        v = self.cli("show interface")
        for s in v.split("\nInterface "):
            match = self.rx_int.search(s)
            if match:
                ifname = match.group("interface")
                if ifname.startswith("Virtual") or ifname.startswith("Tunnel"):
                    continue
                a_stat = match.group("admin_status").lower() == "up"
                o_stat = match.group("oper_status").lower() == "up"
                alias = match.group("alias")
                match_mac = self.rx_mac.search(s)
                if match_mac:
                    """Hack for PortChannel sub int (it no mac in show interfaces)"""
                    mac = match_mac.group("mac")
                sub = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "description": alias,
                    "mac": mac,
                    "enabled_afi": [],
                    "enabled_protocols": []
                }
                match = self.rx_ip.search(s)
                if match:
                    ip = IPv4(match.group("ip"),
                              netmask=match.group("mask")).prefix
                    sub["ipv4_addresses"] = [ip]
                    sub["enabled_afi"] += ["IPv4"]
                match = self.rx_vlan.search(s)
                if match:
                    vlan = match.group("vlan")
                    sub["vlan_ids"] = [vlan]
                if alias in ospfs:
                    sub["enabled_protocols"] += ["OSPF"]
                phys = ifname.find(".") == -1
                if phys:
                    iftype = types[ifname[0]]
                    iface = {
                        "name": ifname,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        "description": alias,
                        "type": iftype,
                        "mac": mac,
                        "subinterfaces": [sub]
                    }
                    interfaces += [iface]
                    if iftype == "SVI" and ifname.startswith("Vlan"):
                        vid = int(ifname[4:].strip())
                        sub["vlan_ids"] = [vid]
                else:
                    if interfaces[-1]["name"] == interfaces[-1]["subinterfaces"][-1]["name"]:
                        interfaces[-1]["subinterfaces"] = [sub]
                    else:
                        interfaces[-1]["subinterfaces"] += [sub]
            else:
                continue
        return [{"interfaces": interfaces}]
