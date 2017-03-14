# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.MA5300.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

"""
"""
# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Huawei.MA5300.get_interfaces"
    interface = IGetInterfaces

    rx_iface_sep = re.compile(r"^ Vlan ID",
        re.MULTILINE | re.IGNORECASE)
    rx_vlan_id = re.compile(r"^: (?P<vlanid>\d+)$",
        re.MULTILINE | re.IGNORECASE)
    rx_iface = re.compile(
        r"^\s*(?P<port>(Adsl|Ethernet|GigabitEthernet)\d+/\d+/\d+)\s+:"
        r"(?P<descr>.*)", re.MULTILINE)
    rx_adsl_state = re.compile(
        r"^\s*(?P<port>Adsl\d+/\d+/\d+)\s+(?P<state>up|down)", re.MULTILINE)
    rx_vdsl_state = re.compile(
        r"^\s*(?P<port>Vdsl\d+/\d+/\d+)\s+(?P<state>up|down)", re.MULTILINE)
    rx_adsl_line = re.compile(
        r"^\s*(?P<port>Adsl\d+/\d+/\d+)\s+\d+\s+\d+\s+"
        r"(?P<vpi>\d+|-)\s+(?P<vci>\d+|-)\s+", re.MULTILINE)

    def execute(self):
        interfaces = []
        # ADSL ports state
        adsl_state = {}
        v = self.cli("show adsl port state all")
        for match in self.rx_adsl_state.finditer(v):
            adsl_state[match.group("port")] = match.group("state")
        # VDSL ports state
        """
        vdsl_state = {}
        v = self.cli("show vdsl port state all")
        for match in self.rx_vdsl_state.finditer(v):
            vdsl_state[match.group("port")] = match.group("state")
        """
        adsl_line = []
        v = self.cli("show adsl line config all")
        for match in self.rx_adsl_line.finditer(v):
            adsl_line += [match.groupdict()]
        v = self.cli("show interface description all")
        for match in self.rx_iface.finditer(v):
            name = match.group("port")
            description = match.group("descr").strip()
            sub = {
                "name": name,
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": ["BRIDGE"],
                "untagged_vlan": 1,
            }
            if "Adsl" in name:
                sub["enabled_afi"] += ["ATM"]
                if adsl_state.get(name):
                    sub["oper_status"] = adsl_state.get(name) == "up"
                for line in adsl_line:
                    if line["port"] == name:
                        if line["vpi"] != "-":
                            sub["vpi"] = line["vpi"]
                        if line["vci"] != "-":
                            sub["vci"] = line["vci"]
                        break
            iface= {
                "name": name,
                "type": "physical",
                "admin_status": True,
                "oper_status": sub["oper_status"],
                "subinterfaces": [sub],
            }
            if description:
                iface["description"] = description
                iface["subinterfaces"][0]["description"] = description
            interfaces += [iface]

        #v = self.cli("show ip interface\n")
        return [{"interfaces": interfaces}]

