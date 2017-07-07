# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
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
    name = "Eltex.MA4000.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    def execute(self):
        r = []
        t = parse_table(self.cli("show lldp neighbor"), allow_wrap=True)
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
            # Do no remove these lines
            if (chassis_id == "") or (port_id == ""):
                continue
            caps = 0
            for c in i[4].split(","):
                c = c.strip()
                if c:
                    caps |= {
                        "Other": 1, "Repeater": 2, "Bridge": 4,
                        "Access Point": 8, "Router": 16, "Telephone": 32,
                        "Cable Device": 64, "Station only": 128
                    }[c]
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
