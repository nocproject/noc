# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_bfd_sessions
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetBFDSessions


class Script(NOCScript):
    name = "Juniper.JUNOS.get_bfd_sessions"
    implements = [IGetBFDSessions]

    rx_session = re.compile(r"^(?P<peer>\d+\.\d+\.\d+\.\d+)\s+(?P<state>Up|Down)\s+(?P<interface>\S+)\s+(?P<detect>\S+)\s+(?P<tx>\S+)\s+(?P<multi>\S+)", re.MULTILINE)

    def execute(self):
        r = []
        s = self.cli("show bfd session")
        for match in self.rx_session.finditer(s):
            print match.groups()
            r += [{
                "peer": match.group("peer"),
                "state": match.group("state").lower() == "up",
                "interface": match.group("interface"),
                "tx_interval": float(match.group("tx")) * 1000000,
                "multiplier": int(match.group("multi")),
                "detect_time": float(match.group("detect")) * 1000000
                }]
        return r
