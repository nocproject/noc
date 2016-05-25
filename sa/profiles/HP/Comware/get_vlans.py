# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.Comware.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "HP.Comware.get_vlans"
    interface = IGetVlans

    def execute(self):
        vlans = self.strip_first_lines(self.cli("display vlan"), 2)
        vlans = self.expand_rangelist(vlans.replace("(default)", ""))
        r = []
        for v in vlans:
            if int(v) == 1:
                continue
            r += [{
                "vlan_id": int(v),
            }]
        return r
