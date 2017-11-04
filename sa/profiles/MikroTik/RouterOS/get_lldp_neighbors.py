# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors

class Script(BaseScript):
    name = "MikroTik.RouterOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    def execute(self):
        res = []
        device_id = self.scripts.get_fqdn()
        interfaces = []
        for n, f, r in self.cli_detail(
        "/interface print detail without-paging where type=\"ether\""):
            interfaces += [r["name"]]
        # Get neighbors
        neighbors = []
        for n, f, r in self.cli_detail(
        "/ip neighbor print detail without-paging"):
            if r["interface"] not in interfaces:
                continue
            if "mac-address" in r and "mac-address" != "":
                chassis_id_subtype = 4
                chassis_id = r["mac-address"]
            else:
                raise self.NotSupportedError()
            if "interface-name" in r and "interface-name" != "":
                port_subtype = 5
                port = r["interface-name"]
            else:
                continue
                #raise self.NotSupportedError()
            caps = 0
            
            if "system-caps" in r and "system-caps" != "":
        	for c in r["system-caps"].split(","):
                    c = c.strip()
                    if not c:
                        break
                    # Need more examples
                    caps |= {
                        "other": 1,
                        "repeater": 2,
                        "bridge": 4,
                        #"WLAN Access Point": 8,
                        "router": 16,
                        "telephone": 32,
                        #"DOCSIS Cable Device": 64,
                        #"Station Only": 128
                    }[c]
            interface = {
                "local_interface": r["interface"],
                "neighbors": [{
                    "remote_chassis_id_subtype": chassis_id_subtype,
                    "remote_chassis_id": chassis_id,
                    "remote_port_subtype": port_subtype,
                    "remote_port": port.replace("GigaEthernet","Gig"),
                    "remote_capabilities": caps,
                }]
            }
            if "system-description" in r:
                interface["neighbors"][0]["remote_system_description"] = \
                r["system-description"]
            res += [interface]
        return res
