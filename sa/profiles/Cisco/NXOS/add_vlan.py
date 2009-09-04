# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.NXOS.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IAddVlan

class Script(noc.sa.script.Script):
    name="Cisco.NXOS.add_vlan"
    implements=[IAddVlan]
    def execute(self,vlan_id,name):
        if self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.configure():
            self.cli("vlan %d"%vlan_id)
            self.cli("name %s"%name)
            self.cli("exit")
        self.save_config()
        return True
