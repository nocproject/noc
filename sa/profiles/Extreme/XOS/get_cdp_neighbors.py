# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_cdp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python module
import re
#
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors


class Script(BaseScript):
    name = "Extreme.XOS.get_cdp_neighbors"
    interface = IGetCDPNeighbors

    rx_dev_id = re.compile("CDP Device ID\s+:\s+(?P<device_id>\S+)")
    rx_entry = re.compile(
        r"^\s*(?P<local_interface>\d+(\:\d+)?)\s+(?P<device_id>\S+)\s+\d+\s+"
        r"Ver\S+\s+(?P<remote_interface>.+)", re.MULTILINE)
    rx_ex_stack_port1 = re.compile("^Slot:\s*(\d+),\s*Port:\s*(\d+)\s*")
    rx_mac = re.compile(r"^System MAC:\s+(?P<mac>\S+)$", re.MULTILINE)

    def normalize_port(self, port):
        if self.rx_ex_stack_port1.match(port):
            # Format Extreme stack: Slot:  1, Port: 24
            return "%s:%s" % self.rx_ex_stack_port1.match(port).groups()
        return port.strip()

    def execute(self):
        match = self.rx_dev_id.search(self.cli("show cdp"))
        device_id = match.group("device_id")
        if device_id == "System":  # DeviceID is System MAC
            device_id = self.rx_mac.search(self.cli("show switch", cached=True))
            if device_id:
                device_id = device_id.group("mac")

        neighbors = []
        for match in self.rx_entry.finditer(self.cli("show cdp ports")):
            neighbors += [match.groupdict()]
            neighbors[-1]["remote_interface"] = self.normalize_port(neighbors[-1]["remote_interface"])
        return {
            "device_id": device_id,
            "neighbors": neighbors
        }
