# ---------------------------------------------------------------------
# Qtech.QSW.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.validators import is_int, is_ipv4, is_mac


class Script(BaseScript):
    name = "Qtech.QSW.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_line = re.compile(
        r"^Interface Ethernet (?P<interface>\S+)\s*\n"
        r"^Port\s+LLDP:\s+\S+\s+Pkt\s+Tx:\s+\d+\s+Pkt\s+Rx:\s+\d+\s*\n"
        r"^Total neighbor count: \d+\s*\n\n"
        r"^Neighbor \(\d+\):\s*\n"
        r"^TTL: \d+\(s\)\s*\n"
        r"^Chassis ID:\s+(?P<chassis_id>\S+)\s*\n"
        r"^Port ID:( port)? (?P<port_id>\S+)\s*\n"
        r"^System Name: (?P<name>\S+)\s*\n"
        r"(^System Description: (?P<system_description>.+)\s*\n)?"
        r"(^Port Description: (?P<port_description>.+)\s*\n)?",
        re.MULTILINE,
    )

    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

    def execute_cli(self, **kwargs):
        r = []

        # Fallback to CLI
        try:
            lldp = self.cli("show lldp interface")
        except self.CLISyntaxError:
            raise NotImplementedError
        for match in self.rx_line.finditer(lldp):
            local_interface = match.group("interface")
            remote_chassis_id = match.group("chassis_id")
            remote_port = match.group("port_id")
            remote_system_name = match.group("name")
            system_description = match.group("system_description")
            port_description = match.group("port_description")

            # Build neighbor data
            # Get capability
            cap = 0
            """
            for c in match.group("capabilities").split(","):
            if cap:
                c = c.strip()
                if c:
                    cap |= {
                        "O": 1, "r": 2, "B": 4,
                        "W": 8, "R": 16, "T": 32,
                        "C": 64, "S": 128, "D": 256,
                        "H": 512, "TP": 1024,
                    }[c]
            """
            # Get remote port subtype
            remote_port_subtype = 5
            if is_ipv4(remote_port):
                # Actually networkAddress(4)
                remote_port_subtype = 4
            elif is_mac(remote_port):
                # Actually macAddress(3)
                remote_port_subtype = 3
            elif is_int(remote_port):
                # Actually local(7)
                remote_port_subtype = 7

            i = {"local_interface": local_interface, "neighbors": []}
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_port": remote_port,
                "remote_capabilities": cap,
                "remote_port_subtype": remote_port_subtype,
            }
            if remote_system_name and remote_system_name != "NULL":
                n["remote_system_name"] = remote_system_name
            if system_description and system_description != "NULL":
                n["remote_system_description"] = system_description
            if port_description and port_description != "NULL":
                n["remote_port_description"] = port_description

            # TODO:
            #            n["remote_chassis_id_subtype"] = 4

            i["neighbors"].append(n)
            r.append(i)
        return r
