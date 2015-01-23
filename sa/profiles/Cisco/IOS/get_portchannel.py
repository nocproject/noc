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

    # Member 0 : GigabitEthernet0/2 , Full-duplex, 1000Mb/s
    rx_po2_members = re.compile(
        r"^\s+Member\s+\d+\s+:\s+(?P<interface>.+?)\s+.*$")

    def execute(self):
        r = []
        try:
            s = self.cli("show interfaces status | i ^Po[0-9]+")
        except self.CLISyntaxError:
            # one more try
            try:
                s = self.cli("show interfaces description | i ^Po[0-9]+_")
            except self.CLISyntaxError:
                return []
            for l in s.splitlines():
                pc, rest = l.split(" ", 1)
                pc = pc[2:]
                v = self.cli("show interfaces port-channel {0} | i Member_[0-9]+".format(pc))
                out_if = {
                    "interface": "Po %s" % pc,
                    "members": [],
                    "type": "S",  # <!> TODO: port-channel type detection
                }
                for line in v.splitlines():
                    match = self.rx_po2_members.match(line)
                    if match:
                        out_if["members"].append(match.group('interface'))
                r += [out_if]
                return r
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
