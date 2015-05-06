# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_udld_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import NOCScript
from noc.sa.interfaces.igetudldneighbors import IGetUDLDNeighbors


class Script(NOCScript):
    name = "Cisco.IOSXR.get_udld_neighbors"
    implements = [IGetUDLDNeighbors]

    rx_split = re.compile(r"^Interface\s+", re.MULTILINE | re.IGNORECASE)
    rx_entry = re.compile(
        r"^\s+Detection\sFSM\sstate:\s+(?P<state>\w+).*"
        r"^\s+Device\sID:\s+(?P<remote_device>.+)\n"
        r"^\s+Device\sname:\s+.+\n"
        r"^\s+Port\sID:\s+(?P<remote_interface>.+)\n"
        r"^\s+Message\sinterval:.+\n"
        r"^\s+Timeout\sinterval:.+\n"
        r"^\s+Echo\s\d+:\s+(?P<local_device>.+),\s(?P<local_interface>.+)\n",
        re.MULTILINE | re.IGNORECASE | re.DOTALL
    )

    def execute(self):
        r = []
        try:
            s = self.cli("show ethernet udld interfaces")
        except self.CLISyntaxError:
            return []
        for p in self.rx_split.split(s):
            match = self.rx_entry.search(p)
            if not match:
                continue
            r += [{
                  "local_device": match.group("local_device"),
                  "local_interface": match.group("local_interface"),
                  "remote_device": match.group("remote_device"),
                  "remote_interface": match.group("remote_interface"),
                  "state": match.group("state").upper()
            }]
        return r
