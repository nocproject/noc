# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_cdp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetCDPNeighbors
import re


class Script(noc.sa.script.Script):
    name = "Cisco.IOSXR.get_cdp_neighbors"
    implements = [IGetCDPNeighbors]
    rx_entry = re.compile(r"Device\sID:\s(?P<device_id>\S+).+"
        r"Interface:\s(?P<local_interface>\S+)\nPort\sID\s"
        r"\(outgoing port\):\s(?P<remote_interface>\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self):
        device_id = self.scripts.get_fqdn()
        s = self.cli("show cdp neighbors detail")
        # Get neighbors
        neighbors = []
        for match in self.rx_entry.finditer(s):
            neighbors += [{
                "device_id": match.group("device_id"),
                "local_interface": match.group("local_interface"),
                "remote_interface": match.group("remote_interface")
            }]
        return {
            "device_id": device_id,
            "neighbors": neighbors
        }

