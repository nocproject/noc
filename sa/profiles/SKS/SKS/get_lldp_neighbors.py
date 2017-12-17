# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.lib.validators import is_ipv4, is_ipv6, is_mac
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "SKS.SKS.get_lldp_neighbors"
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
            elif is_mac(chassis_id):
                chassis_id_subtype = 4
            else:
                chassis_id_subtype = 7
            port_id = i[2]
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = 4
            elif is_mac(port_id):
                port_id_subtype = 3
            else:
                port_id_subtype = 7
            caps = 0
            for c in i[4].split(","):
                c = c.strip()
                if c:
                    caps |= {
                        "O": 1, "P": 2, "B": 4,
                        "W": 8, "R": 16, "r": 16, "T": 32,
                        "C": 64, "S": 128
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
