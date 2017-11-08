# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Carelink.SWG.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.lib.validators import is_ipv4, is_ipv6, is_mac
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Carelink.SWG.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_line = re.compile(
        r"Local port\s+: Port (?P<port>\d+)\s*\n"
        r"Chassis ID\s+: (?P<chassis_id>\S+)\s*\n"
        r"Port ID\s+: (?P<port_id>\S+)\s*\n"
        r"Port Description\s+:(?P<port_description>.*)\n"
        r"System Name\s+:(?P<system_name>.*)\n"
        r"System Description\s+:(?P<system_description>.*)\n"
        r"System Capabilities\s+:(?P<caps>.+)\n")

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp info")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_line.finditer(v):
            chassis_id = match.group("chassis_id")
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = 5
            elif is_mac(chassis_id):
                chassis_id_subtype = 4
            else:
                chassis_id_subtype = 7
            port_id = match.group("port_id")
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = 4
            elif is_mac(port_id):
                port_id_subtype = 3
            else:
                port_id_subtype = 7
            caps = 0
            # Need more examples
            if "Bridge" in match.group("caps"):
                caps += 4
            if "Router" in match.group("caps"):
                caps += 16
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": caps
            }
            if match.group("system_name"):
                neighbor["remote_system_name"] = \
                    match.group("system_name").strip()
            if match.group("system_description"):
                neighbor["remote_system_description"] = \
                    match.group("system_description").strip()
            if match.group("port_description"):
                neighbor["remote_port_description"] = \
                    match.group("port_description").strip()
            r += [{
                "local_interface": match.group("port"),
                "neighbors": [neighbor]
            }]
        return r
