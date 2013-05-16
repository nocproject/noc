# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
# Force10.SFTOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
from noc.lib.text import parse_table


class Script(NOCScript):
    name = "Force10.SFTOS.get_vlans"
    implements = [IGetVlans]

    def execute(self):
        return [{
            "vlan_id": x[0],
            "name":x[1]
        } for x in parse_table(self.cli("show vlan brief"))]
