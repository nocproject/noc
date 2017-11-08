# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_lacp_neighbors
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
    name = "Huawei.VRP.get_lacp_neighbors"
    interface = IGetLACPNeighbors
    split_re = re.compile(r"(\S+)'s state information is:", re.IGNORECASE)

    def execute(self):
        r = []
        try:
            v = self.cli("display eth-trunk")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        first = True
        pc_name = ""
        for block in self.split_re.split(v):
            # print("Split %s" % self.split_re.split(v))
            if not block:
                continue
            if first:
                first = False
                pc_name = block
                continue
            self.logger.info("Block is: %s" % block)
            out = self.profile.parse_table(block)
            self.logger.info("Out, %s" % out)
            i = 0
            bundle = []
            if "Local" not in out:
                first = True
                continue
            for bun in out["Local"]["table"]:
                if i == 0:
                    i += 1
                    continue
                # print("Bundle %s" % bun)
                bundle += [{
                    "interface": bun[0],
                    "local_port_id": int(bun[4]),
                    "remote_system_id": out["Partner"]["table"][i][2],
                    "remote_port_id": int(out["Partner"]["table"][i][4])
                }]
                i += 1

            r += [{"lag_id": int(out["Local"]["LAG ID"]),
                   "interface": pc_name,
                   "system_id": out["Local"]["System ID"],
                   "bundle": bundle
                   }]
            first = True

        return r
