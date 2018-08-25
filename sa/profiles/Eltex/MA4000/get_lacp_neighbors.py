# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors


class Script(BaseScript):
    name = "Eltex.MA4000.get_lacp_neighbors"
    interface = IGetLACPNeighbors

    rx_cg = re.compile(
        r"^Channel group \d+\s*\n"
        r"^\s*Mode: LACP\s*\n",
        re.MULTILINE
    )
    rx_members = re.compile(
        r"^\s*Channel group.*\n"
        r"^\s*Actor System\s+Partner System\s*\n"
        r"^\s*System Priority:.*\n"
        r"^\s*System MAC:\s+(?P<sys_id>\S+)\s+(?P<remote_sys_id>\S+)\s*\n"
        r"^\s*Key:.*\n\n"
        r"^\s*Port (?P<interface>.+):.*\n"
        r"^\s*Actor Port\s+Partner Port\s*\n"
        r"^\s*Port Number:\s+(?P<local_port_id>\d+)\s+(?P<remote_port_id>\d+)\s*\n"
        r"^\s*Port Priority:.*\n"
        r"^\s*LACP Activity:.*\n",
        re.MULTILINE
    )

    def execute(self):
        r = []
        for cg in range(1, 9):
            c = self.cli("show channel-group lacp %s" % cg)
            match = self.rx_cg.search(c)
            if match:
                i = {
                    "lag_id": cg,
                    "interface": "port-channel %s" % cg,
                    "bundle": []
                }
                for match1 in self.rx_members.finditer(c):
                    if match1.group("remote_sys_id") == "00:00:00:00:00:00":
                        continue
                    bundle = {
                        "interface": match1.group("interface"),
                        "local_port_id": match1.group("local_port_id"),
                        "remote_system_id": match1.group("remote_sys_id"),
                        "remote_port_id": match1.group("remote_port_id"),
                    }
                    i["system_id"] = match1.group("sys_id")
                    i["bundle"] += [bundle]
                if i["bundle"]:
                    r += [i]
        return r
