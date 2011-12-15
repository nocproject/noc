# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.SPS2xx.get_portchannel
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
    name = "Linksys.SPS2xx.get_portchannel"
    implements = [IGetPortchannel]

    rx_trunk = re.compile(
        r"^(?P<port>ch\d+)\s+(?P<type1>\S+):\s+(?P<interfaces1>\S+)+(\s+(?P<type2>\S+):\s+(?P<interfaces2>\S+)$|$)",
        re.MULTILINE)

    def execute(self):
        r = []
        # Try SNMP first
        # TODO snmp support

        # Fallback to CLI
        port_channel = self.cli("show interfaces port-channel")
        for match in self.rx_trunk.finditer(port_channel):
            typ = match.group("type1")
            mem = match.group("interfaces1").split('/')
            l = len(mem)
            mem1 = self.expand_rangelist(mem[l - 1])
            members = []
            mem2 = ''
            for j in range(l - 1):
                mem2 += mem[j] + '/'
            for i in mem1:
                members.append(mem2 + str(i))
            mem = match.group("interfaces2")
            if mem:
                typ = match.group("type2")
                mem = mem.split('/')
                l = len(mem)
                mem1 = self.expand_rangelist(mem[l - 1])
                mem2 = ''
                for j in range(l - 1):
                    mem2 += mem[j] + '/'
                for i in mem1:
                    members.append(mem2 + str(i))
            r += [{"interface": match.group("port"),
                    # TODO batter type detection
                    "type": "L" if typ == "Non-candidate" else "S",
                    "members": members,
                }]
        return r
