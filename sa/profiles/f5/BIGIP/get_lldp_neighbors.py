# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors


class Script(NOCScript):
    name = "f5.BIGIP.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    def execute(self):
        r = []
        v = self.cli("show /net lldp-neighbors")
        for h, data in self.parse_blocks(v):
            for row in data.splitlines():
                lp, rc, rp = row.split(None, 2)
                r += [{
                    "local_interface": lp,
                    "neighbors": [{
                        "remote_chassis_id": rc,
                        "remote_port": rp,
                        "remote_capabilities": 0
                    }]
                }]
        return r
