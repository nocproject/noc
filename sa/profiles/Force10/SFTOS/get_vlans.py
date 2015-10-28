# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
# Force10.SFTOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Force10.SFTOS.get_vlans"
    interface = IGetVlans

    def execute(self):
        return [{
            "vlan_id": x[0],
            "name": x[1]
        } for x in parse_table(self.cli("show vlan brief"))]
