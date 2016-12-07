# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_ndp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetndpneighbors import IGetNDPNeighbors


class Script(BaseScript):
    name = "Huawei.VRP.get_ndp_neighbors"
    interface = IGetNDPNeighbors

    neigh_split = re.compile(r"^\sInterface:\s", re.IGNORECASE)

    neigh = re.compile(r"\s*MAC\sAddress\s*:\s(?P<device_id>\S+).+?"
                       r"\s*Port\sName\s*:\s(?P<interface>\S+).+?"
                       r"\s*Device\sName\s*:\s(?P<device_name>\s\S+).+?", re.MULTILINE)

    def execute(self, **kwargs):
        v = self.cli("display ndp ne")

        neighbors = self.neigh_split.split(v)
        for b in neighbors:
            match = self.neigh(b)

        return []