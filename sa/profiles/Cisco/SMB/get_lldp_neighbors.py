# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.SMB.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.lib.validators import is_int, is_ipv4, is_ipv6, is_mac
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Cisco.ISMB.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_neighbor = re.compile(
        r"^Device ID:\s*(?P<remote_chassis_id>\S+)\s*\n"
        r"^Port ID:\s*(?P<remote_port>.+?)\s*\n"
        r"^Capabilities:\s*(?P<caps>.+?)\s*\n",
        re.MULTILINE)
    rx_system_name = re.compile(
        r"^System Name:(?P<system_name>.*)\n", re.MULTILINE)
    rx_port_descr = re.compile(
        r"^Port description:(?P<port_descr>.*)\n", re.MULTILINE)

    def execute_cli(self):
        r = []
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        t = parse_table(v, allow_wrap=True)
        for i in t:
            local_if = i[0]
            v = self.cli("show lldp neighbors %s" % local_if)
            match = self.rx_neighbor.search(v)
            remote_chassis_id = match.group("remote_chassis_id")
            if is_ipv4(remote_chassis_id) or is_ipv6(remote_chassis_id):
                # Actually networkAddress(4)
                remote_chassis_id_subtype = 5
            elif is_mac(remote_chassis_id):
                # Actually macAddress(3)
                # Convert MAC to common form
                remote_chassis_id_subtype = 4
            else:
                remote_chassis_id_subtype = 7
            remote_port = match.group("remote_port")
            if is_ipv4(remote_port) or is_ipv6(remote_port):
                # Actually networkAddress(4)
                remote_port_subtype = 4
            elif is_mac(remote_port):
                # Actually macAddress(3)
                remote_port_subtype = 3
            elif is_int(remote_port):
                # Actually local(7)
                remote_port_subtype = 7
            else:
                remote_port_subtype = 5
            # Get capability
            cap = 0
            s = match.group("caps")
            for c in s.strip().split(", "):
                cap |= {
                    "Other": 1, "Repeater": 2, "Bridge": 4,
                    "WLAN": 8, "Router": 16, "Telephone": 32,
                    "Cable": 64, "Station": 128
                }[c]
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_chassis_id_subtype": remote_chassis_id_subtype,
                "remote_port": remote_port,
                "remote_port_subtype": remote_port_subtype,
                "remote_capabilities": cap
            }
            match = self.rx_system_name.search(v)
            if match and match.group("system_name"):
                n["remote_system_name"] = match.group("system_name")
            match = self.rx_port_descr.search(v)
            if match and match.group("port_descr"):
                n["remote_port_description"] = match.group("port_descr")
            i = {
                "local_interface": local_if,
                "neighbors": [n]
            }
            r += [i]
        return r
