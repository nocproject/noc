# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.IronWare.get_fdp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetFDPNeighbors


class Script(BaseScript):
    """
    Brocade.IronWare.get_fdp_neighbors
    """
    name = "Brocade.IronWare.get_fdp_neighbors"
    interface = IGetFDPNeighbors

    rx_entry = re.compile(r"Device ID: (?P<device_id>\S+).+?"
                          "Interface:\s(?P<local_interface>\S+)\s+Port ID \(outgoing port\): (?P<remote_interface>\S+)",
                          re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self):
        device_id = self.scripts.get_fqdn()
        # Get neighbors
        neighbors = []
        for match in self.rx_entry.finditer(
            self.cli("show fdp neighbors detail")):
            neighbors += [{
                "device_id": match.group("device_id"),
                "local_interface": match.group("local_interface"),
                "remote_interface": match.group("remote_interface")
            }]
        return {
            "device_id": device_id,
            "neighbors": neighbors
        }
