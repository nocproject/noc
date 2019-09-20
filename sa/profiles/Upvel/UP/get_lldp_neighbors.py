# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Upvel.UP.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.validators import is_ipv4, is_ipv6, is_mac
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CAP_BRIDGE,
)


class Script(BaseScript):
    name = "Upvel.UP.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_line = re.compile(
        r"Local Interface\s+: (?P<port>(?:Gi|2.5Gi|10Gi)\S+ \S+)\s*\n"
        r"Chassis ID\s+: (?P<chassis_id>\S+)\s*\n"
        r"Port ID\s+: (?P<port_id>\S+)\s*\n"
        r"Port Description\s+:(?P<port_description>.*)\n"
        r"System Name\s+:(?P<system_name>.*)\n"
        r"System Description\s+:(?P<system_description>.*)\n"
        r"System Capabilities\s+:(?P<caps>.+)\n"
    )

    def execute_cli(self):
        r = []
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_line.finditer(v):
            chassis_id = match.group("chassis_id")
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
            else:
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
            port_id = match.group("port_id")
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_MAC
            else:
                port_id_subtype = LLDP_PORT_SUBTYPE_LOCAL
            caps = 0
            # Need more examples
            if "Bridge" in match.group("caps"):
                caps += LLDP_CAP_BRIDGE
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": caps,
            }
            if match.group("system_name"):
                neighbor["remote_system_name"] = match.group("system_name").strip()
            if match.group("system_description"):
                neighbor["remote_system_description"] = match.group("system_description").strip()
            if match.group("port_description"):
                neighbor["remote_port_description"] = match.group("port_description").strip()
            r += [{"local_interface": match.group("port"), "neighbors": [neighbor]}]
        return r
