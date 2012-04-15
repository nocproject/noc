# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel


class Script(NOCScript):
    name = "Force10.FTOS.get_portchannel"
    implements = [IGetPortchannel]

    rx_first = re.compile(
        r"^\s*(?P<lacp>L?)\s+(?P<port>\d+)\s+\S+\s+(?:up|down)\s+\S+\s+(?P<interface>\S+\s+\S+)\s+\((Up|Down)\)\s*\*?$")
    rx_next = re.compile(
        r"^\s+(?P<interface>\S+\s+\S+)\s+\((Up|Down)\)\s*\*?$")

    def execute(self):
        r = []
        try:
            v = self.cli("show interface port-channel brief")
        except self.CLIOperationError:
            return []
        for l in v.splitlines():
            match = self.rx_first.match(l)
            if match:
                r += [{
                    "interface": "Po %s" % match.group("port"),
                    "type": "L" if match.group("lacp") == "L" else "S",
                    "members": [match.group("interface")]
                }]
                continue
            match = self.rx_next.match(l)
            if match:
                r[-1]["members"] += [match.group("interface")]
                continue
        return r
