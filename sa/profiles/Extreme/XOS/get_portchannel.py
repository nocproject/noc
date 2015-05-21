# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel
import re


class Script(NOCScript):
    name = "Extreme.XOS.get_portchannel"
    implements = [IGetPortchannel]
    rx_trunk = re.compile(r"Group ID\s+:\s+(?P<trunk>\d+).+?Type\s+:\s+(?P<type>\S+).+?Member Port\s+:\s+(?P<members>\S+).+?Status\s+:\s+(?P<status>\S+)", re.MULTILINE | re.DOTALL)
    rx_sh_master = re.compile(r"^\s+(?P<trunk>\d+)+\s+(\d+\s+)?(?P<type>\S+)\s+\S+\s+(?P<member>\d+)\s+\S\s+(?P<status>\S).+", re.IGNORECASE | re.DOTALL)
    rx_sh_member = re.compile(r"^\s+Members:\s+(?P<members>\S+).+", re.IGNORECASE | re.DOTALL)
    def execute(self):
        try:
            t = self.cli("show sharing")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for tt in t.strip().split("\n"):
          match = self.rx_sh_master.search(tt)
          if match:
                try:
                    mem = self.cli("show port %s information detail | include Members" % match.group("trunk"))
                except self.CLISyntaxError:
                    raise self.NotSupportedError()
                memmatch = self.rx_sh_member.search(mem)
                if memmatch:
                     tr_members = self.expand_interface_range(memmatch.group("members"))
                else:
                     tr_members = self.expand_interface_range(match.group("member"))
                r += [{
                    "interface": "T%s" % match.group("trunk"),
                    "members": tr_members,
                    "type": "L" if match.group("type").lower() == "lacp" else "S"
                    }]
        return r
