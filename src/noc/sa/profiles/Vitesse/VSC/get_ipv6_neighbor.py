# ---------------------------------------------------------------------
# Vitesse.VSC.get_ipv6_neighbor
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetipv6neighbor import IGetIPv6Neighbor


class Script(BaseScript):
    name = "Vitesse.VSC.get_ipv6_neighbor"
    interface = IGetIPv6Neighbor

    rx_line = re.compile(
        r"^(?P<ip>[0-9a-fA-F:\.]+) via (?P<interface>\S+):\s+(?P<mac>\S+)\s+(?P<state>\S+)\s*$"
    )

    s_map = {
        "INCMP": "incomplete",
        "Permanent/REACHABLE": "reachable",
        "STALE": "stale",
        "DELAY": "delay",
        "PROBE": "probe",
    }

    def execute(self, vrf=None):
        # Get states
        cmd = "show ipv6 neighbor"
        r = self.cli(cmd, list_re=self.rx_line)
        # Remap states
        for n in r:
            n["state"] = self.s_map[n["state"]]
        return r
