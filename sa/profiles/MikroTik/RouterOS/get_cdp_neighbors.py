# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_cdp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_cdp_neighbors"
    interface = IGetCDPNeighbors

    def execute(self):
        device_id = self.scripts.get_fqdn()
        interfaces = []
        for n, f, r in self.cli_detail(
        "/interface print detail without-paging where type=\"ether\""):
            interfaces += [r["name"]]
        # Get neighbors
        neighbors = []
        for n, f, r in self.cli_detail(
        "/ip neighbor print detail without-paging"):
            platform = r["platform"]
            if platform == "MikroTik":
                continue
            if r["interface"] not in interfaces:
                continue
            neighbors += [{
                "device_id": r["identity"],
                "local_interface": r["interface"],
                "remote_interface": r["interface-name"],
                "remote_ip": r["address"],
                "platform": platform
            }]
        return {
            "device_id": device_id,
            "neighbors": neighbors
        }
