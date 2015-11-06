# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4


class Script(BaseScript):
    name = "Vyatta.Vyatta.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    CHASSIS_SUBTYPE = {
        "mac": 4
    }

    PORT_SUBTYPE = {
        "mac": 3
    }

    def execute(self):
        r = []
        i = {}
        # @todo: Check LLDP is not enabled
        try:
            v = self.cli("show lldp neighbors detail")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for l in v.splitlines():
            if ":" not in l:
                continue
            k, v = [x.strip() for x in l.split(":", 1)]
            if k == "Interface":
                name = v.split(",")[0].strip()
                if i:
                    r += [i]
                i = {
                    "local_interface": name,
                    "neighbors": []
                }
            elif k == "ChassisID":
                ct, cid = [x.strip() for x in v.split()[:2]]
                i["neighbors"] += [{
                    "remote_chassis_id_subtype": self.CHASSIS_SUBTYPE[
                        ct
                    ],
                    "remote_chassis_id": cid
                }]
            elif k == "SysName":
                i["neighbors"][-1]["remote_system_name"] = v
            elif k == "PortID":
                pt, pid = [x.strip() for x in v.split()[:2]]
                i["neighbors"][-1]["remote_port_subtype"] = self.PORT_SUBTYPE[pt]
                i["neighbors"][-1]["remote_port"] = pid
        if i:
            r += [i]
        return r
