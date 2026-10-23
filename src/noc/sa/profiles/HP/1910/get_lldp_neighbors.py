# ---------------------------------------------------------------------
# HP.1910.get_lldp_neighbors
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
    name = "HP.1910.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_line = re.compile(
        r"^\s*LLDP neighbor-information of port \d+\[(?P<interface>\S+)\]:.\s+Neighbor index\s+:\s+\d+.\s+"
        r"Update time\s+:\s+\d+ days,\d+ hours,\d+ minutes,\d+ seconds.\s+Chassis type\s+:\s+"
        r"(?P<chassis_type>(\S+ \S+ \S+|\S+ \S+|\S+)).\s+Chassis ID\s+:\s+(?P<chassis_id>\S+).\s+"
        r"Port ID type\s+:\s+(?P<port_type>(\S+ \S+ \S+|\S+ \S+|\S+)).\s+Port ID\s+:\s+(?P<port_id>\S+).\s+"
        r"Port description\s+:\s+(\S+ \S+ \S+|\S+ \S+|\S+).\s+System name\s+:\s+(?P<name>\S+)",
        re.DOTALL | re.MULTILINE,
    )

    rx_capabilities = re.compile(
        r"^\s+System capabilities enabled\s+:\s+(?P<capabilities>\S+)\s*", re.DOTALL | re.MULTILINE
    )

    def execute_cli(self, **kwargs):
        r = []
        # Fallback to CLI
        lldp = self.cli("display lldp neighbor-information")
        lldp = lldp.splitlines()
        for i in range(len(lldp) - 9):
            line = ""
            for j in range(9):
                line = line + "\n" + lldp[i + j]

            match = self.rx_line.search(line)
            if match:
                local_interface = match.group("interface")
                remote_chassis_id = match.group("chassis_id")
                remote_port = match.group("port_id")
                remote_port = remote_port.replace("gi", "Gi ")
                remote_system_name = match.group("name")

                # Get remote chassis id subtype
                chassis_type = match.group("chassis_type")
                if chassis_type == "MAC address":
                    remote_chassis_id_subtype = 4
                # Get remote port subtype
                port_type = match.group("port_type")
                if port_type == "Interface name":
                    remote_port_subtype = 3
                if port_type == "Locally assigned":
                    remote_port_subtype = 7

                # Build neighbor data
                # Get capability
                while not self.rx_capabilities.search(lldp[i]):
                    i += 1
                match = self.rx_capabilities.search(lldp[i])
                cap = 0
                for c in match.group("capabilities").split(","):
                    c = c.strip()
                    if c:
                        cap |= {
                            "O": 1,
                            "Repeater": 2,
                            "Bridge": 4,
                            "W": 8,
                            "Router": 16,
                            "T": 32,
                            "Telephone": 32,
                            "C": 64,
                            "S": 128,
                            "D": 256,
                            "H": 512,
                            "TP": 1024,
                        }[c]

                i = {"local_interface": local_interface, "neighbors": []}
                n = {
                    "remote_chassis_id": remote_chassis_id,
                    "remote_port": remote_port,
                    "remote_capabilities": cap,
                    "remote_port_subtype": remote_port_subtype,
                    "remote_chassis_id_subtype": remote_chassis_id_subtype,
                    "remote_system_name": remote_system_name,
                }

                i["neighbors"].append(n)
                r.append(i)
        return r
