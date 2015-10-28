# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "DLink.DxS.get_vlans"
    interface = IGetVlans

    def execute(self):
        r = []
        vlans = self.profile.get_vlans(self)
        for v in vlans:
            r += [{
                "vlan_id": v['vlan_id'],
                "name": v['vlan_name']
            }]
        return r
