# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel
import re


class Script(NOCScript):
    name = "DLink.DxS.get_portchannel"
    implements = [IGetPortchannel]
    rx_trunk = re.compile(r"Group ID\s+:\s+(?P<trunk>\d+).+?Type\s+:\s+(?P<type>\S+).+?Member Port\s+:\s+(?P<members>\S+).+?Status\s+:\s+(?P<status>\S+)", re.MULTILINE | re.DOTALL)

    def execute(self):
        try:
            t = self.cli("show link_aggregation")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for match in self.rx_trunk.finditer(t):
            if match.group("status").lower() == "enabled":
                r += [{
                    "interface": "T%s" % match.group("trunk"),
                    "members": self.expand_rangelist(match.group("members")),
                    "type": "L" if match.group("type").lower() == "lacp" else "S"
                    }]
        return r
