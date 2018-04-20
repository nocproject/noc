# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Cisco.NXOS.get_cdp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors
import re


class Script(BaseScript):
    name = "Cisco.NXOS.get_cdp_neighbors"
    interface = IGetCDPNeighbors
    rx_entry = re.compile(r"Device ID:\s?(?P<device_id>\S+).+?"
                          r"Interface: (?P<local_interface>\S+),\s+Port ID "
                          r"\(outgoing port\): (?P<remote_interface>\S+)",
                          re.MULTILINE | re.DOTALL | re.IGNORECASE)
=======
##----------------------------------------------------------------------
## Cisco.NXOS.get_cdp_neighbors
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
    name = "Cisco.NXOS.get_cdp_neighbors"
    implements = [IGetCDPNeighbors]
    rx_entry = re.compile(r"Device ID:\s?(?P<device_id>\S+).+?"
        r"Interface: (?P<local_interface>\S+),\s+Port ID "
        r"\(outgoing port\): (?P<remote_interface>\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        device_id = self.scripts.get_fqdn()
        # Get neighbors
        neighbors = []

        for match in self.rx_entry.finditer(self.cli("show cdp neighbors detail | no-more")):
<<<<<<< HEAD
            device_id = match.group("device_id")
            if "(" in device_id:
                device_id = device_id.split("(")[0]
            neighbors += [{
                "device_id": device_id,
=======
            neighbors += [{
                "device_id": match.group("device_id"),
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                "local_interface": match.group("local_interface"),
                "remote_interface": match.group("remote_interface")
            }]
        return {
            "device_id": device_id,
            "neighbors": neighbors
        }
