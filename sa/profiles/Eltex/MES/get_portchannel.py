# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel

class Script(NOCScript):
    name = "Eltex.MES.get_portchannel"
    implements = [IGetPortchannel]

    rx_trunk = re.compile(r"^(?P<port>Po\d)\s+(?P<type>\S+):\s+(?P<interfaces>\S+)$", re.IGNORECASE | re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_trunk.finditer(self.cli("show interfaces port-channel")):
            typ = match.group("type")
            mem = match.group("interfaces").split('/')
            mem1 = self.expand_rangelist(mem[1])
            members = []
            for i in mem1:
                members.append(mem[0] + '/' + str(i))
            print typ
            r += [{
                "interface" : match.group("port"),
                "type"      : "L" if typ == "Non-candidate" else "S",
                "members"   : members,
            }]
        return r
