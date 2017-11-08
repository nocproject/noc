# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.AOS.get_lacp_neighbors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors


class Script(BaseScript):
    name = "Alcatel.AOS.get_lacp_neighbors"
    interface = IGetLACPNeighbors

    def execute(self):
        r = []
        d = {}
        for lag in self.scripts.get_portchannel():
            bundle = []
            for port in lag["members"]:
                try:
                    v = self.cli("show linkagg port %s" % port)
                except self.CLISyntaxError:
                    raise self.NotSupportedError()
                d = {l.split(":", 1)[0].strip(): l.split(":", 1)[1].strip() for l in v.splitlines() if ":" in l}
                bundle += [{
                    "interface": port,
                    "local_port_id": int(d["Actor Port"].strip(",")) + 1024,
                    "remote_system_id": d["Partner Oper System Id"].strip(",[]"),
                    "remote_port_id": d["Partner Oper Port"].strip(",")
                }]
            if not lag["members"]:
                return []
            r += [{"lag_id": lag["interface"],
                   "interface": "Ag " + lag["interface"],
                   "system_id": d["Actor System Id"].strip(",[]"),
                   "bundle": bundle
                   }]
        return r
