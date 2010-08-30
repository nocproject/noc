# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetPortchannel
import re

rx_first=re.compile(r"^\s*(?P<lacp>L?)\s+(?P<port>\d+)\s+\S+\s+(?:up|down)\s+\S+\s+(?P<interface>\S+\s+\S+)\s+\((Up|Down)\)\s*\*?$")
rx_next=re.compile(r"^\s+(?P<interface>\S+\s+\S+)\s+\((Up|Down)\)\s*\*?$")


class Script(noc.sa.script.Script):
    name="Force10.FTOS.get_portchannel"
    implements=[IGetPortchannel]
    def execute(self):
        r=[]
        for l in self.cli("show interface port-channel brief").splitlines():
            match=rx_first.match(l)
            if match:
                r+=[{
                    "interface": "Po %s"%match.group("port"),
                    "type"     : "L" if match.group("lacp")=="L" else "S",
                    "members"  : [match.group("interface")]
                }]
                continue
            match=rx_next.match(l)
            if match:
                r[-1]["members"]+=[match.group("interface")]
                continue
        return r
