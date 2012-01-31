# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetLLDPNeighbors
import re

rx_sep = re.compile(r"^===+\n", re.MULTILINE)
rx_local_interface = re.compile(
    r"Local interface (?P<interface>\S+\s+\S+) has \d+ neighbor",
    re.IGNORECASE | re.MULTILINE)
rx_nsep = re.compile(r"\n*-----+\n+")
rx_remote_chassis_id_subtype = re.compile(
    r"Remote Chassis ID Subtype:.+\((?P<subtype>\d+)\)",
    re.IGNORECASE | re.MULTILINE)
rx_remote_chassis_id = re.compile(r"Remote Chassis ID:\s*(?P<id>\S+)",
    re.IGNORECASE | re.MULTILINE)
rx_remote_port_id_subtype = re.compile(
    r"Remote Port Subtype:.+\((?P<subtype>\d+)\)",
     re.IGNORECASE | re.MULTILINE)
rx_remote_port_id = re.compile(r"Remote Port ID:\s*(?P<port>.+?)$",
    re.IGNORECASE | re.MULTILINE)
rx_remote_system_name = re.compile(r"Remote System Name:\s*(?P<name>\S+)",
    re.IGNORECASE | re.MULTILINE)
rx_remote_capabilities = re.compile(
    r"Enabled System Capabilities:\s*(?P<capabilities>.*?)$",
    re.IGNORECASE | re.MULTILINE)


class Script(noc.sa.script.Script):
    name = "Force10.FTOS.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    def execute(self):
        r = []
        v = self.cli("show lldp neighbors detail")
        # For each interface
        for s in rx_sep.split(v)[1:]:
            match = rx_local_interface.search(s)
            if not match:
                continue
            sr = {"local_interface": match.group("interface"), "neighbors": []}
            # For each interface neighbor
            for ns in rx_nsep.split(s)[1:-1]:
                n = {}
                # Get remote chassis id subtype
                match = rx_remote_chassis_id_subtype.search(ns)
                if not match:
                    continue
                n["remote_chassis_id_subtype"] = int(match.group("subtype"))
                # Get remote chassis id
                match = rx_remote_chassis_id.search(ns)
                if not match:
                    continue
                n["remote_chassis_id"] = match.group("id")
                # Get remote port id subtype
                match = rx_remote_port_id_subtype.search(ns)
                if not match:
                    continue
                n["remote_port_subtype"] = int(match.group("subtype"))
                # Get remote port id
                match = rx_remote_port_id.search(ns)
                if not match:
                    continue
                n["remote_port"] = match.group("port").strip()
                # Get remote system name
                match = rx_remote_system_name.search(ns)
                if match:
                    n["remote_system_name"] = match.group("name")
                # Get capabilities
                caps = 0
                match = rx_remote_capabilities.search(ns)
                if match:
                    for c in match.group("capabilities").split():
                        caps |= {
                            "other": 1, "repeater": 2, "bridge": 4,
                            "wlanaccesspoint": 8, "router": 16,
                            "telephone": 32, "docsis": 64, "station": 128
                        }[c.lower()]
                n["remote_capabilities"] = caps
                sr["neighbors"] += [n]
            r += [sr]
        return r
