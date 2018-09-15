# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Siklu.EH.get_interfaces"
    cache = True
    interface = IGetInterfaces

    IFINDEX = {
        "host": 1,
        "eth0": 2,
        "eth1": 3,
        "eth2": 4,
        "eth3": 5,
        "eth4": 6
    }

    rx_ecfg = re.compile(
        r"^(?P<cmd>\S+)\s+(?P<name>\S+)\s+(?P<key>\S+)\s*:(?P<value>.*?)$",
        re.MULTILINE)
    rx_vlan = re.compile(
        r"^\s*\S+\s+(?P<vlanid>\d+)\s+\d+\s+(?P<vlans>\S+)\s+(?P<untagged>\S+)\s+\S+\s*\n",
        re.MULTILINE)

    def parse_section(self, section):
        r = {}
        name = None
        for match in self.rx_ecfg.finditer(section):
            name = match.group("name")
            r[match.group("key")] = match.group("value").strip()
        return name, r

    def execute(self):
        v = self.cli("show eth all")
        ifaces = []
        for section in v.split("\n\n"):
            if not section:
                continue
            name, cfg = self.parse_section(section)
            i = {
                "name": name,
                "type": "physical",
                "mac": cfg["mac-addr"],
                "description": cfg["description"],
                "admin_status": cfg["admin"] == "up",
                "oper_status": cfg["operational"] == "up",
                "subinterfaces": [{
                    "name": name,
                    "mac": cfg["mac-addr"],
                    "description": cfg["description"],
                    "admin_status": cfg["admin"] == "up",
                    "oper_status": cfg["operational"] == "up",
                    "enabled_afi": ["BRIDGE"],
                    "tagged_vlans": []
                }]
            }
            if name in self.IFINDEX:
                i["snmp_ifindex"] = self.IFINDEX[name]
            ifaces += [i]
        c = self.cli("show vlan")
        for match in self.rx_vlan.finditer(c):
            vlan_id = int(match.group('vlanid'))
            if vlan_id == 1:
                continue
            for i in ifaces:
                if i["name"] in match.group("vlans").split(","):
                    if i["name"] == match.group("untagged"):
                        i["subinterfaces"][0]["untagged_vlan"] = vlan_id
                    else:
                        i["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
        v = self.cli("show ip all")
        for section in v.split("\n\n"):
            if not section:
                continue
            name, cfg = self.parse_section(section)
            ip = cfg["ip-addr"]
            if "static" in ip:
                ip = ip.replace("static", "").strip()
            ip_addr = "%s/%s" % (ip, cfg["prefix-len"])
            i = {
                "name": name,
                "type": "SVI",
                "admin_status": True,
                "oper_status": True,
                "subinterfaces": [{
                    "name": name,
                    "admin_status": True,
                    "oper_status": True,
                    "ipv4_addresses": [ip_addr],
                    "enabled_afi": ["IPv4"]
                }]
            }
            if cfg["vlan"]:
                if int(cfg["vlan"]) > 0:
                    i["subinterfaces"][0]["vlan_ids"] = int(cfg["vlan"])
            ifaces += [i]
        return [{"interfaces": ifaces}]
