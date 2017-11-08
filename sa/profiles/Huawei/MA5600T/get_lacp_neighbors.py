# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors


class Script(BaseScript):
    name = "Huawei.MA5600T.get_lacp_neighbors"
    interface = IGetLACPNeighbors

    rx_bundle = re.compile(
        r"^\s+Port Number\s+: (?P<local_port_id>\S+)\s*\n"
        r"^\s+Selected AggID : \d+\s*\n"
        r"^\s+System ID\s+: \d+, (?P<system_id>\S+)\s*\n"
        r".+\n"
        r"^Partner\s*\n"
        r"^\s+System ID\s+: \d+, (?P<remote_system_id>\S+)\s*\n"
        r"^\s+Port Number\s+: (?P<remote_port_id>\S+)\s*\n",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        r = []
        for pc in self.scripts.get_portchannel():
            lacp = {
                "lag_id": pc["interface"],
                "interface": pc["interface"],
                "bundle": []
            }
            for port in pc["members"]:
                c = self.cli("display lacp link-aggregation port %s" % port)
                match = self.rx_bundle.search(c)
                lacp["system_id"] = match.group("system_id")
                lacp["bundle"] += [{
                    "interface": port,
                    "local_port_id": match.group("local_port_id"),
                    "remote_system_id": match.group("remote_system_id"),
                    "remote_port_id": match.group("remote_port_id")
                }]
            r += [lacp]
        return r
