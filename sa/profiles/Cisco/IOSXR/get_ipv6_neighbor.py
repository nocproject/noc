# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Cisco.IOSXR.get_ipv6_neighbor
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetipv6neighbor import IGetIPv6Neighbor


class Script(BaseScript):
    name = "Cisco.IOSXR.get_ipv6_neighbor"
    interface = IGetIPv6Neighbor
=======
##----------------------------------------------------------------------
## Cisco.IOSXR.get_ipv6_neighbor
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetIPv6Neighbor


class Script(NOCScript):
    name = "Cisco.IOSXR.get_ipv6_neighbor"
    implements = [IGetIPv6Neighbor]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_line = re.compile(
        r"^(?P<ip>[0-9a-fA-F:\.]+)\s+"
        r"\d+\s+"
        r"(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+"
        r"(?P<state>\S+)\s+"
        r"(?P<interface>\S+)\s*$")

    s_map = {
        "INCMP": "incomplete",
        "REACH": "reachable",
        "STALE": "stale",
        "DELAY": "delay",
        "PROBE": "probe",
        "DELETE": "incomplete",
        "GLEAN": "incomplete"
    }

    def execute(self, vrf=None):
        # Get states
        cmd = "show ipv6 neighbors"
        r =  self.cli(cmd, list_re=self.rx_line)
        # Remap states
        for n in r:
            n["state"] = self.s_map[n["state"].upper()]
        return r
