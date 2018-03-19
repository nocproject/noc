# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_cdp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Extreme.XOS.get_cdp_neighbors"
    interface = IGetCDPNeighbors

    rx_dev_id = re.compile("CDP Device ID\s+:\s+(?P<device_id>\S+)")
    rx_entry = re.compile(
        r"^\s*(?P<local_interface>\d+(\:\d+)?)\s+(?P<device_id>\S+)\s+\d+\s+"
        r"Ver\S+\s+(?P<remote_interface>\S+)", re.MULTILINE)
    rx_rem_ports = re.compile("Slot:\s*(?P<slot>\d+)\s*,\s*Port\s*:\s*(?P<port>\d+)")
    rx_mac = re.compile(r"^System MAC:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute(self):
        match = self.rx_dev_id.search(self.cli("show cdp"))
        device_id = match.group("device_id")
        if device_id == "System":  # DeviceID is System MAC
            device_id = self.rx_mac.search(self.cli("show switch", cached=True))
            if device_id:
                device_id = device_id.group("mac")
        neighbors = []
        for match in parse_table(self.cli("show cdp ports")):
            """
            New format - is table:
            Port  Device-Id            Hold time  Remote CDP  Port ID
                                      Version
            ----  -------------------  ---------  ----------  --------------------
            1:49  02:XX:XX:XX:XX:XX    165        Version-2   Slot:  1, Port: 49

            """
            if not match or not self.rx_rem_ports.match(match[4]):
                continue
            neighbors += [{"device_id": match[1],
                           "local_interface": match[0],
                           "remote_interface": "%s:%s" % self.rx_rem_ports.match(match[4]).groups()
                           }]

        return {
            "device_id": device_id,
            "neighbors": neighbors
        }
