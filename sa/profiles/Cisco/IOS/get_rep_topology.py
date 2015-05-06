# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_rep_topology
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetREPTopology


class Script(NOCScript):
    name = "Cisco.IOS.get_rep_topology"
    implements = [IGetREPTopology]
    rx_port = re.compile("^(?P<host>\S+), (?P<port>\S+)\s+\((?P<role>[^)]+)\)\n"
                         "\s+(?P<state>Open|Alternate|Failed) Port,.+?\n"
                         "\s+Bridge MAC: (?P<mac>\S+)\n"
                         "\s+.+?\n"
                         "\s+.+?\n"
                         "\s+Neighbor Number:\s+(?P<fwd>\d+)\s*/\s*\[-(?P<rev>\d+)\]",
        re.MULTILINE)

    s_map = {
        "open": "OPEN",
        "alternate": "ALT",
        "failed": "FAIL"
    }

    def execute(self):
        try:
            s = self.cli("show rep topology detail")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        if not s.strip():
            return r
        for rs in s.split("REP Segment "):
            if not rs:
                continue
            # Fetch segment number
            sn, ports = rs.split("\n", 1)
            rs = {
                "segment": int(sn),
                "topology": []
            }
            # Parse ports
            for match in self.rx_port.finditer(ports):
                role = match.group("role").lower()
                if "primary" in role:
                    edge = "PRI"
                elif "secondary" in role:
                    edge = "SEC"
                else:
                    edge = None
                no_neighbor = "no-neighbor" in role
                rs["topology"] += [{
                    "name": match.group("host"),
                    "mac": match.group("mac"),
                    "port": match.group("port"),
                    "role": self.s_map[match.group("state").lower()],
                    "edge_no_neighbor": no_neighbor,
                    "neighbor_number": int(match.group("fwd")),
                    "rev_neighbor_number": int(match.group("rev"))
                }]
                if edge:
                    rs["topology"][-1]["edge"] = edge
            r += [rs]
        return r
