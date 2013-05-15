# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Arista.EOS.get_portchannel
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
    name = "Arista.EOS.get_portchannel"
    implements = [IGetPortchannel]

    rx_portchannel = re.compile(
        r"Port Channel (?P<portchannel>Port-Channel\d+):\n"
        r"\s+Active Ports:\s+(?P<members>[^\n]+)\n",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        r = []
        v = self.cli("show port-channel", file="/tmp/pc")
        for match in self.rx_portchannel.finditer(v):
            members = match.group("members").strip().split()
            members = [m for m in members if not m.startswith("Peer")]
            r += [{
                "interface": match.group("portchannel"),
                "type": "L",
                "members": members
            }]
        return r
