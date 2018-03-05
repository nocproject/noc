# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.7302.get_spanning_tree
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree
import re


class Script(BaseScript):
    name = "Alcatel.7302.get_spanning_tree"
    interface = IGetSpanningTree

    # Split block by "port-info"
    split_re = re.compile(r"port-info\s*(?P<params>.*)", re.IGNORECASE)
    # Get key:value STP parameter
    k_v_re = re.compile(r"(?P<key>\S+)\s*:\s*(?P<value>\S+)", re.IGNORECASE)

    def execute(self):
        r = {"mode": "RSTP",
             "instances": []}

        instance = {"id": 0,
                    "vlans": "1-4095",
                    "interfaces": []}
        try:
            # RSTP
            v = self.cli("show rstp port-info detail")
        except self.CLISyntaxError:
            try:
                # MSTP
                v = self.cli("show mstp port-instance detail")
            except self.CLISyntaxError:
                r["instances"] += [instance]
                return r

        for e in self.split_re.split(v):
            if "stp bridge parameters" in e:
                # Common parameter block
                kv = dict(self.k_v_re.findall(v))
                instance.update(
                    {
                        "root_id": kv["designated-root"].split(":", 2)[2],
                        "root_priority": int("".join(kv["designated-root"].split(":", 2)[:2]), 16),
                        "bridge_id": kv["designated-root"].split(":", 2)[2],
                        "bridge_priority": int("".join(kv["designated-root"].split(":", 2)[:2]), 16)
                    })
            elif "stp port parameters" in e:
                # Port parameter block
                kv = dict(self.k_v_re.findall(e))
                print kv
                instance["interfaces"] += [{
                    "interface": "ethernet:%d" % (int(kv["port"]) + 1),
                    "port_id": "%d.%s" % (int(kv["designated-port"].split(":")[0], 16),
                                          int(kv["designated-port"].split(":")[1], 16)),
                    "state": kv["state"],
                    "role": kv["role"],
                    "priority": int("".join(kv["designated-bridge"].split(":", 2)[:2]), 16),
                    "designated_bridge_id": kv["designated-bridge"].split(":", 2)[2],
                    "designated_bridge_priority": int(kv["designated-port"].split(":")[0], 16),
                    "designated_port_id": "%d.%s" % (int(kv["designated-port"].split(":")[0], 16),
                                                     int(kv["designated-port"].split(":")[1], 16)),
                    "point_to_point": kv["oper-p2p"] == "p2p",
                    "edge": kv["oper-edge-port"] != "no-edge-port"
                }]
        r["instances"] += [instance]
        return r
