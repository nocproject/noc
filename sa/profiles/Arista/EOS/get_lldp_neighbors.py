# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Arista.EOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors


class Script(NOCScript):
    name = "Arista.EOS.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_isep = re.compile(r"^Interface\s+", re.MULTILINE)
    rx_nsep = re.compile(r"^\s+Neighbor\s+", re.MULTILINE)
    rx_n = re.compile(
        r"\s+- Chassis ID type:\s+[^(]+\((?P<chassis_id_subtype>\d+)\).+?"
        r"\s+Chassis ID\s+:\s+(?P<chassis_id>[^\n]+).+?"
        r"\s+- Port ID type:\s+[^(]+\((?P<port_id_type>\d+)\).+?"
        r"\s+Port ID\s+:\s+(?P<port_id>[^\n]+)",
        re.MULTILINE | re.DOTALL
    )
    rx_system_name = re.compile(
        r"^\s+- System Name: \"(?P<sysname>[^\"]+)\"",
        re.MULTILINE
    )

    rx_caps = re.compile(
        r"^\s+Enabled Capabilities:\s+(?P<caps>[^\n]+)",
        re.MULTILINE
    )

    def execute(self):
        def unq(s):
            if s and s.startswith("\"") and s.endswith("\""):
                return s[1:-1]
            else:
                return s

        r = []
        try:
            v = self.cli("show lldp neighbors detailed")
        except self.CLIOperationError:
            return []  # LLDP is not enabled
        # For each interface
        for s in self.rx_isep.split(v)[1:]:
            sr = {
                "local_interface": s.split(" ", 1)[0],
                "neighbors": []
            }
            # For each neighbor
            for ns in self.rx_nsep.split(s)[1:]:
                n = {}
                match = self.rx_n.search(ns)
                if not match:
                    continue
                n["remote_chassis_id_subtype"] = int(match.group("chassis_id_subtype"))
                n["remote_chassis_id"] = unq(match.group("chassis_id"))
                n["remote_port_subtype"] = int(match.group("port_id_type"))
                n["remote_port"] = unq(match.group("port_id"))
                match = self.rx_system_name.search(ns)
                if match:
                    n["remote_system_name"] = match.group("sysname")
                # Get capabilities
                caps = 0
                match = self.rx_caps.search(ns)
                if match:
                    for c in match.group("caps").split(", "):
                        caps |= {
                            "other": 1, "repeater": 2, "bridge": 4,
                            "wlanaccesspoint": 8, "router": 16,
                            "telephone": 32, "docsis": 64,
                            "station": 128
                        }[c.lower()]
                n["remote_capabilities"] = caps
                sr["neighbors"] += [n]
            r += [sr]
        return r
