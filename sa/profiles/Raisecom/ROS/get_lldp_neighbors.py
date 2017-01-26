# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raisecom.ROS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4


class Script(BaseScript):
    name = "Raisecom.ROS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_lldp = re.compile(
        r"^\s*Port\s+port(?P<port>\d+)\s*has\s+1\s*remotes:\n\n"
        r"^\s*Remote\s*1\s*\n"
        r"^\s*\-+\n"
        r"^\s*ChassisIdSubtype:\s+(?P<ch_type>\S+)\s*\n"
        r"^\s*ChassisId:\s+(?P<ch_id>\S+)\s*\n"
        r"^\s*PortIdSubtype:\s+(?P<port_id_subtype>\S+)\s*\n"
        r"^\s*PortId:\s+(?P<port_id>.+)\s*\n"
        r"^\s*PortDesc:\s+(?P<port_descr>.+)\s*\n"
        r"^\s*SysName:\s+(?P<sys_name>.+)\s*\n"
        r"^\s*SysDesc:\s+(?P<sys_descr>.+)\n"
        r"^\s*SysCapSupported:\s+(?P<sys_caps_supported>\S+)\s*\n"
        r"^\s*SysCapEnabled:\s+(?P<sys_caps_enabled>\S+)\s*\n",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
        r = []
        v = self.cli("show lldp remote detail")
        for match in self.rx_lldp.finditer(v):
            i = {"local_interface": match.group("port"), "neighbors": []}
            cap = 0
            for c in match.group("sys_caps_enabled").strip().split(","):
                cap |= {
                    "Other": 1,
                    "Repeater/Hub": 2,
                    "Bridge/Switch": 4,
                    "Router": 16,
                    "Station": 128
                }[c]
            n = {
                "remote_chassis_id_subtype": {
                        "macAddress": 4,
                        "networkAddress": 5
                    }[match.group("ch_type")],
                "remote_chassis_id": match.group("ch_id"),
                "remote_port_subtype": {
                    "ifAlias": 1,
                    "macAddress": 3,
                        "ifName": 5,
                        "local": 7
                    }[match.group("port_id_subtype")],
                "remote_port": match.group("port_id"),
                "remote_capabilities": cap
            }
            if match.group("sys_name") != "N/A":
                n["remote_system_name"] = match.group("sys_name")
            if match.group("sys_descr") != "N/A" and "\n" not in match.group("sys_descr"):
                sd = match.group("sys_descr")
                if "SysDesc:" in sd:
                    sd = sd.split()[-1]
                n["remote_system_description"] = sd
            if match.group("port_descr") != "N/A":
                n["remote_port_description"] = match.group("port_descr")
            i["neighbors"] += [n]
            r += [i]
        return r
