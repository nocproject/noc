# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_cdp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors


class Script(NOCScript):
    name = "Cisco.IOSXR.get_cdp_neighbors"
    implements = [IGetCDPNeighbors]
    rx_split = re.compile("^--------+\n", re.MULTILINE)

    def execute(self):
        device_id = self.scripts.get_fqdn()
        s = self.cli("show cdp neighbors detail")
        r = []
        for n in self.rx_split.split(s)[1:]:
            neighbor = {}
            for l in n.splitlines():
                sl = l.lower()
                if sl.startswith("device id"):
                    neighbor["device_id"] = l.split(":", 1)[-1].strip()
                elif sl.startswith("interface"):
                    neighbor["local_interface"] = l.split(":", 1)[-1].strip()
                elif sl.startswith("port id"):
                    neighbor["remote_interface"] = l.split(":", 1)[-1].strip()
            r += [neighbor]
        return {
            "device_id": device_id,
            "neighbors": r
        }
