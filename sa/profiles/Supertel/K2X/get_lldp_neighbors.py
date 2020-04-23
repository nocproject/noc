# ---------------------------------------------------------------------
# Supertel.K2X.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Supertel.K2X.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_lldp = re.compile(
        r"^(?P<interface>g\d+)\s+(?P<chassis_id>\S+)\s+(?P<port_id>\S+)\s+"
        r"((?P<name>\S+)\s+|)(?P<capabilities>\S+)\s*$",
        re.MULTILINE,
    )

    def execute_cli(self, **kwargs):
        r = []
        # Fallback to CLI
        lldp = self.cli("show lldp neighbors")
        for match in self.rx_lldp.finditer(lldp):
            local_interface = match.group("interface")
            remote_chassis_id = match.group("chassis_id")
            remote_port = match.group("port_id")
            remote_system_name = match.group("name")
            cap = 0
            for c in match.group("capabilities").split(","):
                c = c.strip()
                if c:
                    cap |= {"O": 1, "r": 2, "B": 4, "W": 8, "R": 16, "T": 32, "D": 256, "H": 512}[c]
                # Get remote port subtype
                remote_port_subtype = 5
                #                remote_port_subtype = 7

                i = {"local_interface": local_interface, "neighbors": []}
                n = {
                    "remote_chassis_id": remote_chassis_id,
                    "remote_port": remote_port,
                    "remote_capabilities": cap,
                    "remote_port_subtype": remote_port_subtype,
                }
                if remote_system_name:
                    n["remote_system_name"] = remote_system_name

                i["neighbors"].append(n)
                r.append(i)
        return r
