# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans

class Script(NOCScript):
    name="Huawei.VRP.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        self.cli("undo terminal logging")
        v=self.cli("display vlan")
        vlans=", ".join(v.splitlines()[1:])
        vlans=vlans.replace("(default)","")
        return [{"vlan_id":int(x)} for x in self.expand_rangelist(vlans)]
    
