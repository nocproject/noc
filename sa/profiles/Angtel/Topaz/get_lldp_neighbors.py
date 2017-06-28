# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Angtel.Topaz.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4, is_ipv6
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Angtel.Topaz.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_line = re.compile(
        r"^(?P<port>(?:Gi|Te|Po)\S+)\s+(?P<system_id>\S+)\s+"
        r"(?P<port_id>\S+)\s+(?P<system_name>.*)\s+(?P<caps>\S+)\s+\d+",
        re.IGNORECASE)

    CAPS = {
        "": 0, "O": 1, "r": 2,
        "B": 4, "W": 8, "R": 16,
        "T": 32, "D": 64, "H": 128
    }

    def execute(self):
        r = []
        data = []
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        v = v.replace("\n\n", "\n")
        for l in parse_table(v):
            if not l[0]:
                data[-1] = [s[0]+s[1] for s in zip(data[-1], l)]
                continue
            data += [l]

        for d in data:
                chassis_id = d[1]
                if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                        chassis_id_subtype = 5
                else:
                        try:
                            MACAddressParameter().clean(chassis_id)
                            chassis_id_subtype = 4
                        except ValueError:
                            chassis_id_subtype = 7
                port_id = d[2]
                if is_ipv4(port_id) or is_ipv6(port_id):
                        port_id_subtype = 4
                else:
                        try:
                            MACAddressParameter().clean(port_id)
                            port_id_subtype = 3
                        except ValueError:
                            port_id_subtype = 7
                caps = sum([self.CAPS[s.strip()] for s in d[4].split(",")])

                neighbor = {
                    "remote_chassis_id": chassis_id,
                    "remote_chassis_id_subtype": chassis_id_subtype,
                    "remote_port": port_id,
                    "remote_port_subtype": port_id_subtype,
                    "remote_capabilities": caps
                }
                """
                if match.group("system_name"):
                    neighbor["remote_system_name"] = match.group("system_name")
                """
                neighbor["remote_system_name"] = d[3]
                r += [{
                    # "local_interface": match.group("port"),
                    "local_interface": d[0],
                    "neighbors": [neighbor]
                }]

        return r
