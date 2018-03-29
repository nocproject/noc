# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors


class Script(BaseScript):
    name = "Extreme.XOS.get_lacp_neighbors"
    interface = IGetLACPNeighbors
    split_re = re.compile(r"(\S+)'s state information is:", re.IGNORECASE)
    system_id = re.compile(r"System MAC\s*:\s*(?P<system_id>\S+)")

    @staticmethod
    def get_local_id(port_name):
        # Local id for stack: 1:49 -> 1049, for non-stack ?
        if ":" in port_name:
            return int("%s0%s" % tuple(port_name.split(":")))
        return int(port_name)

    def execute(self):
        r = []
        bundle = []

        try:
            v = self.cli("show lacp")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        system_mac = self.system_id.search(v).group(1)
        lags_table = self.profile.parse_table_struct(v, header_start="Lag",
                                                     table_start="-------",
                                                     table_end="=======")

        i = 1  # LAG ID, where you...
        for lag in lags_table:
            if not lag["Lag "]:
                continue
            v = self.cli("show lacp lag %s" % lag["Lag "][0])
            info = self.profile.parse_table_struct(v.split("Port list:")[0],
                                                   header_start="Lag",
                                                   table_start="-------",
                                                   table_end="=======")
            for b in self.profile.parse_table_struct(v.split("Port list:")[1],
                                                     header_start="Member",
                                                     table_start="-------",
                                                     table_end="======="):
                bundle += [{
                    "interface": b["Member Port"][0],
                    "local_port_id": self.get_local_id(b["Member Port"][0]),
                    "remote_system_id": info[0]["Partner MAC"][0],
                    "remote_port_id": int(b["Partner Port"][0])
                }]

            r += [{"lag_id": i,
                   "interface": lag["Lag "][0],
                   "system_id": system_mac,
                   "bundle": bundle
                   }]
            i += 1

        return r
