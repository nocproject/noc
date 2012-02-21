# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4


class Script(NOCScript):
    name = "Eltex.MES.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_line = re.compile(
        r"^(?P<interface>\S+)\s+(?P<chassis_id>\S+)\s+(\d+/|)(?P<port_id>\S+)\s+((?P<name>\S+)\s|)+(?P<capabilities>\S+)\s+\d+(\s+|)$",
        re.MULTILINE)
    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

    def execute(self):
        r = []
        # Try SNMP first
        # TODO...

        # Fallback to CLI
        try:
            lldp = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_line.finditer(lldp):
            local_interface = match.group("interface")
            remote_chassis_id = match.group("chassis_id")
            remote_port = match.group("port_id")
            remote_system_name = match.group("name")

            # Build neighbor data
            # Get capability
            cap = 0
            for c in match.group("capabilities").split(","):
                c = c.strip()
                if c:
                    cap |= {
                        "O": 1, "r": 2, "B": 4,
                        "W": 8, "R": 16, "T": 32,
                        "C": 64, "S": 128, "D": 256,
                        "H": 512, "TP": 1024,
                    }[c]

            # Get remote port subtype
            remote_port_subtype = 5
            if self.rx_mac.match(remote_port):
                # Actually macAddress(3)
                # Convert MAC to common form
                remote_port = MACAddressParameter().clean(remote_port)
                remote_port_subtype = 3
            elif is_ipv4(remote_port):
                # Actually networkAddress(4)
                remote_port_subtype = 4
            elif is_int(remote_port):
                # Actually local(7)
#                remote_port_subtype = 7  # Whi 7? 7 don't work!!!
                remote_port_subtype = 5

            i = {"local_interface": local_interface, "neighbors": []}
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_port": remote_port,
                "remote_capabilities": cap,
                "remote_port_subtype": remote_port_subtype,
                }
            if remote_system_name:
                n["remote_system_name"] = remote_system_name

            # TODO:
#            n["remote_chassis_id_subtype"] = 4

            i["neighbors"].append(n)
            r.append(i)
        return r
