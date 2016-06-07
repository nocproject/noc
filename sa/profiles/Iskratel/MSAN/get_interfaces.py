# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Iskratel.MSAN.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(BaseScript):
    name = "Iskratel.MSAN.get_interfaces"
    interface = IGetInterfaces

    rx_if_pvc = re.compile(
        r"^Interface\.+ (?P<port>\S+).+?"
        r"^\s+PVC\n"
        r"^PVC\s+VLAN ID\n"
        r"^------- -------\n"
        r"^(?P<pvcs>(\d+/\d+\s+\d+\n)+)", re.MULTILINE | re.DOTALL)
    rx_pvc = re.compile(
        r"^(?P<vpi>\d+)/(?P<vci>\d+)\s+(?P<vlan>\d+)$", re.MULTILINE)
    rx_svi = re.compile(
        r"^IP Address\.+ (?P<ip>\S+)\n"
        r"^Subnet Mask\.+ (?P<mask>\S+)\n"
        r"^Burned In MAC Address\.+ (?P<mac>\S+)\n"
        r"^Management VLAN ID\.+ (?P<vlan>\d+)\n",
        re.MULTILINE)
    rx_port = re.compile(
        r"^(?P<port>\d+/\d+)\s+(?:\s+|PC|PC Mbr)\s+"
        r"(?P<admin_status>Enable|Disable)\s+"
        r"(?:Auto|1000 Full)\s+"
        r"(?:Auto|1000 Full)\s+"
        r"(?P<oper_status>Up|Down)\s+(?:Enable|Disable)\s+"
        r"(?:Enable|Disable)(?P<descr>.*?)?\n", re.MULTILINE)

    def execute(self):
        pch = self.scripts.get_portchannel()
        pvc = []
        c = self.cli("show interface all pvc")
        for match in self.rx_if_pvc.finditer(c):
            for match1 in self.rx_pvc.finditer(match.group("pvcs")):
                pvc += [{
                    "port":match.group("port"),
                    "vpi": int(match1.group("vpi")),
                    "vci": int(match1.group("vci")),
                    "vlan": int(match1.group("vlan"))
                }]
        interfaces = []
        for match in self.rx_port.finditer(self.cli("show port all")):
            ifname = match.group('port')
            i = {
                "name": ifname,
                "type": "physical",
                "admin_status": match.group('admin_status') == "Enable",
                "oper_status": match.group('oper_status') == "Enable",
                "enabled_protocols": [],
                "subinterfaces": []
            }
            if pch and (ifname == pch[0]["interface"]):
                i["type"] = "aggregated"
            for p in pvc:
                if p["port"] == ifname:
                    s = {
                        "name": ifname,
                        "admin_status": match.group('admin_status') == "Enable",
                        "oper_status": match.group('oper_status') == "Enable",
                        "tagged_vlans": [p["vlan"]],
                        "vpi": p["vpi"],
                        "vci": p["vci"],
                        "enabled_afi": ["BRIDGE", 'ATM']
                    }
                    i["subinterfaces"] += [s]
            if not i["subinterfaces"]:
                s = {
                    "name": ifname,
                    "admin_status": match.group('admin_status') == "Enable",
                    "oper_status": match.group('oper_status') == "Enable",
                    "enabled_afi": ['BRIDGE']
                }
                if pch  and (ifname in pch[0]["members"]):
                    s["aggregated_interface"] = pch[0]["interface"]
                i["subinterfaces"] = [s]
            interfaces += [i]
        match = self.rx_svi.search(self.cli("show network"))
        if match:
            i = {
                "name": "mgmt",
                "type": "SVI",
                "oper_status": True,
                "admin_status": True,
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": "mgmt",
                    "oper_status": True,
                    "admin_status": True,
                    "mac": match.group('mac'),
                    "vlan_ids": [int(match.group('vlan'))],
                    "enabled_afi": ['IPv4']
                }]
            }
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
            interfaces += [i]
        return [{"interfaces": interfaces}]
