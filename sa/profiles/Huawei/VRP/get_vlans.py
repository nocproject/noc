# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans

class Script(noc.sa.script.Script):
    name="Huawei.VRP.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        self.cli("undo terminal logging")
        vlans=self.cli("display vlan").split("\n")
        vlans=vlans[1].replace("(default)","")
        return [{"vlan_id":int(x)} for x in self.expand_rangelist(vlans)]
