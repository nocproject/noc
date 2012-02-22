# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetPortchannel
import re


class Script(noc.sa.script.Script):
    name = "Cisco.IOS.get_portchannel"
    implements = [IGetPortchannel]

    def execute(self):
        r = []
        try:
            s = self.cli("show interfaces status | i ^Po[0-9]+")
        except self.CLISyntaxError:
            return []
        for l in s.splitlines():
            pc, rest = l.split(" ", 1)
            pc = pc[2:]
            v = self.cli("show interfaces port-channel %s | i Members in this channel" % pc).strip()
            if not v:
                continue
            if v.startswith("Members in this channel"):
                x, y = v.split(":", 1)
                r += [{
                    "interface": "Po %s" % pc,
                    "members": y.strip().split(),
                    "type": "L",  # <!> TODO: port-channel type detection
                }]
            else:
                r += [{
                    "interface": "Po %s" % pc,
                    "members": [],
                    "type": "L",  # <!> TODO: port-channel type detection
                }]
        return r
