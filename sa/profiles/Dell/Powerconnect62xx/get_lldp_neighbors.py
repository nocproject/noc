# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dell.Powerconnect62xx.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
# from noc.lib.validators import is_int, is_ipv4
import re


class Script(BaseScript):
    name = "Dell.Powerconnect62xx.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_line = re.compile(
        r"^(?P<interface>\d+\S+)\s+(?P<rem_id>\d+)\s+(?P<chassis_id>\S+)\s+"
        r"(?P<port_id>\d+\S*)\s+(?P<system_name>\S+)\s*$", re.MULTILINE)

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp remote-device all")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        # For each interface
        for match in self.rx_line.finditer(v):
            i = {"local_interface": match.group("interface"), "neighbors": []}
            neighbor = {
                "remote_chassis_id_subtype": match.group("rem_id"),
                "remote_chassis_id": match.group("chassis_id"),
                "remote_port": match.group("port_id"),
                "remote_system_name": match.group("system_name")
            }
            i["neighbors"] += [neighbor]
            r += [i]
        return r
