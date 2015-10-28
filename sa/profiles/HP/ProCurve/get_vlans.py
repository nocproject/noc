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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "HP.ProCurve.get_vlans"
    interface = IGetVlans

    def execute(self):
        v = self.cli("show vlans")
        return [{
            "vlan_id": int(row[0]),
             "name": row[1]
        } for row in parse_table(v)]
