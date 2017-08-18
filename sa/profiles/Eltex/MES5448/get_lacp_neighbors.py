# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES5448.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES5448.get_lacp_neighbors"
    interface = IGetLACPNeighbors

    def execute(self):
        p = self.scripts.get_portchannel()
        if not p:
            return []
        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        r = []
        for i in parse_table(self.cli("show lacp partner all")):
            if i[2] == "00:00:00:00:00:00":
                continue
            bundle = {
                "interface": i[0],
                "local_port_id": 0,  # XXX Can not determine local port id
                "remote_system_id": i[2],
                "remote_port_id": int(i[5])
            }
            found = False
            for iface in r:
                if iface["lag_id"] == i[3]:
                    iface["bundle"] += [bundle]
                    found = True
                    break
            if not found:
                for iface in p:
                    for member in iface["members"]:
                        if member == i[0]:
                            r += [{
                                "lag_id": i[3],  # XXX check this
                                "interface": iface["interface"],
                                "system_id": mac,
                                "bundle": [bundle]
                            }]
                            found = True
                            break
                    if found:
                        break
        return r
