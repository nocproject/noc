# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "DLink.DxS.get_vlans"
    interface = IGetVlans
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        r = []
        vlans = self.profile.get_vlans(self)
        for v in vlans:
<<<<<<< HEAD
            if v['vlan_name']:
                r += [{
                    "vlan_id": v['vlan_id'],
                    "name": v['vlan_name']
                }]
            else:
                r += [{
                    "vlan_id": v['vlan_id']
                }]
=======
            r += [{
                "vlan_id": v['vlan_id'],
                "name": v['vlan_name']
            }]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r
