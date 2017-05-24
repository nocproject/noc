# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_ndp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igethuaweindpneighbors import IGetHuaweiNDPNeighbors


class Script(BaseScript):
    name = "Huawei.VRP.get_huawei_ndp_neighbors"
    interface = IGetHuaweiNDPNeighbors

    neigh_split = re.compile(
        r"^\sInterface:\s",
        re.IGNORECASE | re.MULTILINE
    )

    neigh = re.compile(
        r"^\s*(?P<local_interface>\S+).+?"
        r"^\s*MAC\sAddress\s*:\s(?P<chassis_mac>\S+).+?"
        r"^\s*Port\sName\s*:\s(?P<interface>\S+).+?"
        r"^\s*Device\sName\s*:\s(?P<name>\S+).+?",
        re.MULTILINE | re.DOTALL
    )

    def execute(self, **kwargs):
        data = []
        column = ("chassis_mac", "interface", "name")
        v = self.cli("display ndp")

        neighbors = self.neigh_split.split(v)
        for b in neighbors:
            match = self.neigh.match(b)
            if match:
                n = match.groups()
                data += [{"local_interface": n[0],
                          "neighbors": [dict(zip(column, n[1:]))]}]
        return data
