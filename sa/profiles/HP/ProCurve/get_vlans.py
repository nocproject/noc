# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
from noc.lib.text import parse_table


class Script(NOCScript):
    name = "HP.ProCurve.get_vlans"
    implements = [IGetVlans]

    def execute(self):
        v = self.cli("show vlans")
        return [{
            "vlan_id": int(row[0]),
             "name": row[1]
        } for row in parse_table(v)]
