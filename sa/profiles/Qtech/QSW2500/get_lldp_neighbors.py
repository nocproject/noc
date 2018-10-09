# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2500.get_lldp_neighbors
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
    name = "Qtech.QSW2500.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_int = re.compile(
        r"^Port\s+(?P<interface>\S+) has\s+1 remotes:\s*\n"
        r"^Remote 1\s*\n"
        r"^-+\S*\n"
        r"^ChassisIdSubtype:\s+(?P<chassis_subtype>\S+)\s*\n"
        r"^ChassisId:\s+(?P<chassis_id>\S+)\s*\n"
        r"^PortIdSubtype:\s+(?P<port_subtype>\S+)\s*\n"
        r"^PortId:\s+(?P<port_id>\S+)\s*\n"
        r"^PortDesc:(?P<port_descr>.*)\n"
        r"^SysName:(?P<system_name>.*)\n"
        r"^SysDesc:(?P<system_descr>[\S\s]+)"
        r"^SysCapSupported:.*\n"
        r"^SysCapEnabled:(?P<caps>.*)\n",
        re.MULTILINE
    )
    CHASSIS_TYPE = {
        "macAddress": 4,
        "networkAddress": 5
    }
    PORT_TYPE = {
        "ifName": 1,
        "portComponent": 2,
        "macAddress": 3,
        "nterfaceName": 5,
        "local": 7
    }

    def execute_cli(self):
        result = []
        try:
            c = self.cli("show lldp remote detail")
        except self.CLISyntaxError:
            return {}
        for match in self.rx_int.finditer(c):
            r = {
                "local_interface": match.group("interface"),
                "neighbors": [{
                    "remote_chassis_id_subtype": self.CHASSIS_TYPE[
                        match.group("chassis_subtype")
                    ],
                    "remote_chassis_id": match.group("chassis_id"),
                    "remote_port_subtype": self.PORT_TYPE[
                        match.group("port_subtype")
                    ],
                    "remote_port": match.group("port_id")
                }]
            }
            system_name = match.group("system_name").strip()
            if system_name and system_name != "N/A":
                r["neighbors"][0]["remote_system_name"] = system_name
            system_descr = match.group("system_descr").strip()
            if system_descr and system_descr != "N/A":
                r["neighbors"][0]["remote_system_description"] = system_descr
            port_descr = match.group("port_descr").strip()
            if port_descr and port_descr != "N/A":
                r["neighbors"][0]["remote_port_description"] = system_descr
            cap = 0
            caps = match.group("caps").strip()
            if caps and caps != "N/A":
                # Need more examples
                pass
            # Dummy stub
            r["neighbors"][0]["remote_capabilities"] = cap
            result += [r]
        return result
