# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
# Force10.SFTOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
from noc.lib.text import parse_table


class Script(NOCScript):
    name = "Force10.SFTOS.get_arp"
    implements = [IGetARP]

    def execute(self):
        return [{
            "ip": x[0],
            "mac": x[1],
            "interface": x[2]
        } for x in parse_table(self.cli("show arp"))]
