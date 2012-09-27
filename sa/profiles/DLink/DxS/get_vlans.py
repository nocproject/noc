# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "DLink.DxS.get_vlans"
    implements = [IGetVlans]

    def execute(self):
        r = []
        vlans = self.profile.get_vlans(self)
        for v in vlans:
            r += [{
                "vlan_id": v['vlan_id'],
                "name": v['vlan_name']
            }]
        return r
