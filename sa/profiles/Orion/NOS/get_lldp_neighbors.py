# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Orion.NOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Orion.NOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    """
    Notes:

    On Alpha-A10E ver.4.15.1205 `show lldp remote detail` do not display
    ChassisId field
    """
    rx_lldp = re.compile(r"^port(?P<port>\d+)\s+(?P<chassis_id>\S+)", re.MULTILINE)
    rx_int = re.compile(
        r"^Port\s+port(?P<interface>\d+)\s+has\s+1\s+remotes:\s*\n"
        r"^\s*\n"
        r"^Remote\s*1\s*\n"
        r"^-+\s*\n"
        r"^ChassisIdSubtype\s*:\s+(?P<chassis_subtype>\S+)\s*\n"
        r"(^ChassisId\s*:\s+(?P<chassis_id>\S+)\s*\n)?"  # See Notes
        r"^PortIdSubtype\s*:\s+(?P<port_subtype>\S+)\s*\n"
        r"^PortId\s*:\s+(?P<port_id>.+)\n"
        r"^PortDesc\s*:\s+(?P<port_descr>.+)\n"
        r"^SysName\s*:\s+(?P<sys_name>.+)\n"
        r"^SysDesc\s*:\s+(?P<sys_descr>(.+\n)+)"
        r"^SysCapSupported\s*:.*\n"
        r"^SysCapEnabled\s*:\s+(?P<caps>.+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        result = []
        chassis = {}
        v = self.cli("show lldp remote")
        for match in self.rx_lldp.finditer(v):
            chassis[match.group("port")] = match.group("chassis_id")
        v = self.cli("show lldp remote detail")
        for match in self.rx_int.finditer(v):
            neighbor = {
                "remote_chassis_id_subtype": {"macAddress": 4, "networkAddress": 5, "ifName": 6}[
                    match.group("chassis_subtype")
                ],
                # "remote_chassis_id": match.group("chassis_id"),
                "remote_port_subtype": {
                    "ifAlias": 1,
                    "macAddress": 3,
                    "ifName": 5,
                    "portComponent": 5,
                    "local": 7,
                }[match.group("port_subtype")],
                "remote_port": match.group("port_id"),
            }
            if match.group("chassis_id"):
                neighbor["remote_chassis_id"] = match.group("chassis_id")
            else:
                neighbor["remote_chassis_id"] = chassis[match.group("interface")]
            if match.group("port_descr").strip():
                p = match.group("port_descr").strip()
                neighbor["remote_port_description"] = re.sub(r"\n\s{30}", "", p)
            if match.group("sys_name").strip():
                p = match.group("sys_name").strip()
                neighbor["remote_system_name"] = re.sub(r"\n\s{30}", "", p)
            if match.group("sys_descr").strip():
                p = match.group("sys_descr").strip()
                neighbor["remote_system_description"] = re.sub(r"\n\s{30}", "", p)
            caps = 0
            for c in match.group("caps").split(","):
                c = c.strip()
                if not c:
                    break
                caps |= {
                    "Other": 1,
                    "Repeater/Hub": 2,
                    "Bridge/Switch": 4,
                    "Router": 16,
                    "Telephone": 32,
                    "Station": 128,
                }[c]
            neighbor["remote_capabilities"] = caps
            result += [{"local_interface": match.group("interface"), "neighbors": [neighbor]}]
        return result
