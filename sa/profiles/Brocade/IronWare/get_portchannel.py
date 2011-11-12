# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.IronWare.get_portchannel
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
    """
    Brocade.IronWare.get_portchannel
    """
    name = "Brocade.IronWare.get_portchannel"
    implements = [IGetPortchannel]

    rx_trunk = re.compile(
        r"Trunk\sID\:\s(\d+)\nType:\s(\S+)\n.*\n.*\n.*\nPorts((\s+\d\/\d)+)",
        re.MULTILINE)

    def execute(self):
        r = []
        # Get trunks
        st = self.cli("show trunk")
        for trunk in self.rx_trunk.findall(st):
            r += [{
                "interface": trunk[0],
                "members": trunk[2].split(),
                "type": trunk[1]
            }]
        return r
