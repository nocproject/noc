# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Supertel.K2X.get_ipv6_neighbor
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetipv6neighbor import IGetIPv6Neighbor


class Script(BaseScript):
    name = "Supertel.K2X.get_ipv6_neighbor"
    interface = IGetIPv6Neighbor
=======
##----------------------------------------------------------------------
## Supertel.K2X.get_ipv6_neighbor
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetIPv6Neighbor


class Script(NOCScript):
    name = "Supertel.K2X.get_ipv6_neighbor"
    implements = [IGetIPv6Neighbor]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_line = re.compile(
        r"\s*(?P<interface>\S+)\s+"
        r"(?P<ip>[0-9a-fA-F:\.]+)\s+"
        r"(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+"
        r"(?P<state>\S+)\s*$")

    s_map = {
        "INCMP": "incomplete",
        "REACH": "reachable",
        "STALE": "stale",
        "DELAY": "delay",
        "PROBE": "probe"
    }

    def execute(self, vrf=None):
        # Get states
        r = []
        for cmd in ["show ipv6 neighbors static",
                    "show ipv6 neighbors dynamic"]:
            r += self.cli(cmd, list_re=self.rx_line)
        # Remap states
#        for n in r:
#            n["state"] = self.s_map[n["state"]]
        return r
