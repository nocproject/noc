# ---------------------------------------------------------------------
# HP.ProCurve.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors
from noc.core.text import parse_table


class Script(BaseScript):
    name = "HP.ProCurve.get_lacp_neighbors"
    interface = IGetLACPNeighbors

    rx_system_id = re.compile(r"System ID\s*:\s*(?P<system_id>\S+)")

    def execute_cli(self, **kwargs):
        v = self.cli("show lacp")
        p_map = {}
        for r in parse_table(v):
            p_map[r[0]] = {"key": r[-1], "aggregate": r[2]}
        m = {}
        v = self.cli("show lacp peer")
        sid = self.rx_system_id.search(v).group("system_id")
        for r in parse_table(v):
            lag = self.profile.convert_interface_name(r[1])
            if lag not in m:
                m[lag] = {"lag_id": lag[3:], "interface": lag, "system_id": sid, "bundle": []}
            if r[6] != "Active":
                continue
            lport = self.profile.convert_interface_name(r[0])
            m[lag]["bundle"] += [
                {
                    "interface": lport,
                    "local_port_id": r[5],
                    "remote_system_id": r[2],
                    "remote_port_id": r[3],
                }
            ]
        return list(m.values())
