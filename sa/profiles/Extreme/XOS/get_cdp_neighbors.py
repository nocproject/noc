# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_cdp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors


class Script(BaseScript):
    name = "Extreme.XOS.get_cdp_neighbors"
    interface = IGetCDPNeighbors

    rx_dev_id = re.compile("CDP Device ID\s+:\s+(?P<device_id>\S+)")
    rx_entry = re.compile(
        r"^\s*(?P<local_interface>\d+(\:\d+)?)\s+(?P<device_id>\S+)\s+\d+\s+"
        r"Ver\S+\s+(?P<remote_interface>\S+)", re.MULTILINE)

    def execute(self):
        match = self.rx_dev_id.search(self.cli("show cdp"))
        device_id = match.group("device_id")
        neighbors = []
        for match in self.rx_entry.finditer(self.cli("show cdp ports")):
            neighbors += [match.groupdict()]
        return {
            "device_id": device_id,
            "neighbors": neighbors
        }
