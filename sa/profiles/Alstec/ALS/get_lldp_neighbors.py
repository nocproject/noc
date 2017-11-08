# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.ALS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.lib.validators import is_ipv4, is_ipv6
from noc.sa.interfaces.base import MACAddressParameter
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Alstec.ALS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    blank_line = re.compile(r"^\s{79}\n", re.MULTILINE)

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp neighbors")
            # This is strange behavior, but it helps us
            v = self.blank_line.sub("", v)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        t = parse_table(v, allow_wrap=True, allow_extend=True)
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
                if c:
                    caps |= {
                        "O": 1, "P": 2, "B": 4,
                        "W": 8, "R": 16, "T": 32,
                        "C": 64, "S": 128
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
