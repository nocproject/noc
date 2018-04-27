# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.mac import MAC


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    rx_int = re.compile(r"Table on\s*(?P<interface>\S+)",re.MULTILINE)
    rx_ChassisID = re.compile(r"ChassisID:    \|\s*(?P<chassis_id>\S+)\s\((?P<chassis_subtype>[a-z]*)",re.MULTILINE)
    rx_PortID = re.compile(r"PortID:       \|\s*(?P<port_id>\S+)\s\((?P<port_subtype>[a-zN]*)",re.MULTILINE)
    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

    def execute_cli(self):
        result = []
        try:
            lldp = self.cli("lldp report")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        for match in self.rx_int.finditer(lldp):
            result += [{
                "local_interface": match.group("interface"),
                "neighbors": [{
		    "remote_chassis_id_subtype": {
			"Interface alias": 1,
                        "Port component": 2,
                        "Local": 7,
                        "ifName": 5,
			"mac": 3
		    }[self.rx_ChassisID.search(lldp).group("chassis_subtype")],
                    "remote_chassis_id": self.rx_ChassisID.search(lldp).group("chassis_id"),
                    "remote_port_subtype": {
                        "Interface alias": 1,
                        "Port component": 2,
                        "Local": 7,
                        "ifName": 5,
                        "mac": 3
                    }[self.rx_PortID.search(lldp).group("port_subtype")],
                    "remote_port": self.rx_PortID.search(lldp).group("port_id")
                }]
            }]
        return result
