# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7324RU.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.text import *
from noc.lib.ip import *
from collections import defaultdict


class Script(NOCScript):
    name = "Alcatel.7324RU.get_interfaces"
    implements = [IGetInterfaces]
    rx_vlan = re.compile(
        r" *(?P<vid>\d+)[ ]*(?P<vname>[A-Za-z0-9\-\.]+)\n[ 0-9\n]+"
        r" +(?P<vstatus>enabled|disabled)[ 0-9]+\n([ \-xnf]+)\n"
        r" +(?P<portmask>[\-tu]+)"
        r" *(?P<uplinkmask>[\-tu]*)",
        re.MULTILINE | re.IGNORECASE)
    rx_mac = re.compile(
        r"MAC\saddress:\s(?P<mac>\S+)\s*",
        re.IGNORECASE
    )

    def execute(self):
        # Management ip interface
        ipif = self.cli("ip show")
        mgmt_vlan = self.cli("switch vlan cpu show")
        sys_mac = self.cli("sys info show")
        mac = re.findall(self.rx_mac, sys_mac)[0]
        vl = mgmt_vlan.splitlines()[0].split(":")[1].strip()
        ip = [IPv4(parse_table(ipif)[0][1],
                   netmask=parse_table(ipif)[0][2]).prefix]
        i = [{
            "admin_status": True,
            "enabled_protocols": [],
            "mac": mac,
            "name": vl,
            "oper_status": True,
            "subinterfaces": [{
                "admin_status": True,
                "enabled_afi": ["IPv4"],
                "enabled_protocols": [],
                "ipv4_addresses": ip,
                "mac": mac,
                "name": vl,
                "oper_status": True,
                "vlan_ids": [vl]
            }],
            "type": "SVI"
        }]
        # ADSL ports
        phy_ports = self.cli("adsl show")
        oper_ports = self.cli("statistics adsl show")
        sub_ports = self.cli("adsl pvc show")
        vlans = self.cli("switch vlan show *")
        phy_ports = phy_ports.split("Subscriber Info:")
        for phy in parse_table(phy_ports[0]):
            t1 = parse_table(phy_ports[1])[int(phy[0]) - 1]
            admin_status = False
            oper_status = False
            if phy[1] == "V":
                admin_status = True
            if t1[1] == "V":
                oper_status = True
            description = ""
            if t1[1] != "-":
                description = t1[1] + " " + t1[2]
            sub = []
            for s in parse_table(sub_ports):
                if s[0] == phy[0]:
                    sub += [{
                        "name": s[0],
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["ATM", "BRIDGE"],
                        "description": description,
                        "untagged_vlan": s[3],
                        "vpi": s[1],
                        "vci": s[2]
                    }]
            i += [{
                "name": phy[0],
                "type": "physical",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "description": description,
                "subinterfaces": sub
            }]
        # Enet ports info
        enet_ports = self.cli("statistics enet")
        tagged = defaultdict(list)
        for match in re.finditer(self.rx_vlan, vlans):
            up = 0
            if match.group("vstatus") == "enabled":
                for x in match.group("uplinkmask"):
                    up += 1
                    if x == "T":
                        tagged[up] += [match.group("vid")]
        for y in range(up):
            oper_status = True
            admin_status = True
            if parse_table(enet_ports)[y][1] == "disabled":
                admin_status = False
                oper_status = False
            elif parse_table(enet_ports)[y][1] == "link down":
                oper_status = False
            i += [{
                "name": "enet%d" % (y+1),
                "type": "physical",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "mac": mac,
                "subinterfaces": [{
                    "admin_status": admin_status,
                    "enabled_afi": ["BRIDGE"],
                    "oper_status": oper_status,
                    "name": "enet%d" % (y+1),
                    "mac": mac,
                    "tagged_vlans": tagged[y+1]
                }]
            }]
        return [{"interfaces": i}]
