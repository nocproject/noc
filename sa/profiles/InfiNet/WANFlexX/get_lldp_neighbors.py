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


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    rx_int = re.compile(
        r"Table on\s*(?P<interface>\S+)",
        re.MULTILINE)
    rx_ChassisID = re.compile(
        r"ChassisID:    \|\s*(?P<chassis_id>\S+)\s\((?P<chassis_sub>[a-z]*)",
        re.MULTILINE)
    rx_PortID = re.compile(
        r"PortID:       \|\s*(?P<port_id>\S+)\s\((?P<port_subtype>[a-zN]*)",
        re.MULTILINE)
    rx_PortDescr = re.compile(
        r"PortDescr:    \|\s*(?P<port_descr>.+?)\|",
        re.MULTILINE)
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
                        "chassis component": 1,
                        "interface alias": 2,
                        "port component": 3,
                        "mac": 4,
                        "network address": 5,
                        "interface name": 6,
                        "local": 7
                    }[self.rx_ChassisID.search(lldp).group("chassis_sub").lower()],
                    "remote_chassis_id":
                    self.rx_ChassisID.search(lldp).group("chassis_id"),
                    "remote_port_subtype": {
                        "interface alias": 1,
                        "port component": 2,
                        "mac": 3,
                        "ifname": 5,
                        "local": 7,
                    }[self.rx_PortID.search(lldp).group("port_subtype").lower()],
                    "remote_port": self.rx_PortID.search(lldp).group("port_id"),
                    "remote_port_description": self.rx_PortDescr.search(lldp).group("port_descr").strip()
                }]
            }]
        return result
