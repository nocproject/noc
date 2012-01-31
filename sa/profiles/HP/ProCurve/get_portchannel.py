# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel


class Script(NOCScript):
    name = "HP.ProCurve.get_portchannel"
    implements = [IGetPortchannel]

    rx_trunk = re.compile(r"^\s*(?P<port>\S+)\s*\|.+?\|\s+(?P<trunk>Trk\S+)\s+(?P<type>\S+)\s*$", re.MULTILINE)

    def execute(self):
        r = []
        # Get trunks
        trunks = {}
        trunk_types = {}
        for port, trunk, type in self.rx_trunk.findall(self.cli("show trunks")):
            if trunk not in trunks:
                trunks[trunk] = []
                trunk_types[trunk] = type
            trunks[trunk] += [port]
        # Build result
        for trunk in trunks:
            r += [{
                "interface": trunk,
                "members": trunks[trunk],
                "type": "L" if trunk_types[trunk].lower() == "lacp" else "S"
            }]
        return r
