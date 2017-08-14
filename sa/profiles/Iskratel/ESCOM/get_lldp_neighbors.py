# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4, is_ipv6
from noc.lib.text import parse_table
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Iskratel.ESCOM.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        t = parse_table(v, allow_wrap=True)
        for i in t:
            chassis_id = i[1]
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = 5
            else:
                try:
                    MACAddressParameter().clean(chassis_id)
                    chassis_id_subtype = 4
                except ValueError:
                    chassis_id_subtype = 7
            port_id = i[2]
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = 4
            else:
                try:
                    MACAddressParameter().clean(port_id)
                    port_id_subtype = 3
                except ValueError:
                    port_id_subtype = 7
            caps = 0
            for c in i[4].split(","):
                c = c.strip()
                """
                System capability legend:
                B - Bridge; R - Router; W - Wlan Access Point; T - telephone;
                D - DOCSIS Cable Device; H - Host; r - Repeater;
                TP - Two Ports MAC Relay; S - S-VLAN; C - C-VLAN; O - Other
                """
                if c:
                    caps |= {
                        "TP": 1, "S":1, "C": 1, "O": 1,
                        "r": 2, "B": 4, "W": 8, "R": 16,
                        "T": 32, "D": 64
                    }[c]
            """
            if "O" in i[4]:
                caps += 1
            elif "r" in i[4]:
                caps += 2
            elif "B" in i[4]:
                caps += 4
            elif "W" in i[4]:
                caps += 8
            elif "R" in i[4]:
                caps += 16
            elif "T" in i[4]:
                caps += 32
            elif "D" in i[4]:
                caps += 64
            elif "H" in i[4]:
                caps += 128
            """
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": caps
            }
            if i[3]:
                neighbor["remote_system_name"] = i[3]
            r += [{
                "local_interface": i[0],
                "neighbors": [neighbor]
            }]
        return r
