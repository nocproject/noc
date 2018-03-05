# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.SMB.get_cdp_neighbors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors


class Script(BaseScript):
    name = "Cisco.SMB.get_cdp_neighbors"
    interface = IGetCDPNeighbors
    rx_entry = re.compile(
        r"Device-ID:\s*(?P<device_id>\S+).+?"
        r"Interface: (?P<local_interface>\S+),\s+"
        r"Port ID\s*\(outgoing port\):\s*(?P<remote_interface>\S+).+?"
        r"IP (?P<remote_ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        device_id = self.scripts.get_fqdn()
        # Get neighbors
        neighbors = []
        c = self.cli("show cdp neighbors detail")
        for match in self.rx_entry.finditer(c):
            neighbors += [{
                "device_id": match.group("device_id"),
                "local_interface": match.group("local_interface"),
                "remote_interface": match.group("remote_interface"),
                "remote_ip": match.group("remote_ip")
            }]
        return {
            "device_id": device_id,
            "neighbors": neighbors
        }
