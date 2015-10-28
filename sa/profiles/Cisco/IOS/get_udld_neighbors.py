# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_udld_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetudldneighbors import IGetUDLDNeighbors


class Script(BaseScript):
    name = "Cisco.IOS.get_udld_neighbors"
    interface = IGetUDLDNeighbors

    rx_split = re.compile(r"^Interface\s+", re.MULTILINE | re.IGNORECASE)
    rx_entry = re.compile(
        r"^\s+Current neighbor state:\s+(?P<state>Bidirectional).+?"
        r"^\s+Device (?:ID|name):\s+(?P<remote_device>\S+).+?"
        r"^\s+Port ID:\s+(?P<remote_interface>\S+).+?"
        r"^\s+Neighbor echo \d+ device: (?P<local_device>\S+)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL
    )

    def execute(self):
        r = []
        try:
            s = self.cli("show udld")
        except self.CLISyntaxError:
            return []
        for p in self.rx_split.split(s):
            v = p.split("\n", 1)
            if len(v) != 2 or not v[1].startswith("---"):
                continue
            local_interface = v[0].strip()
            match = self.rx_entry.search(v[1])
            if not match:
                continue
            r += [{
                  "local_device": match.group("local_device"),
                  "local_interface": local_interface,
                  "remote_device": match.group("remote_device"),
                  "remote_interface": match.group("remote_interface"),
                  "state": match.group("state").upper()
            }]
        return r
