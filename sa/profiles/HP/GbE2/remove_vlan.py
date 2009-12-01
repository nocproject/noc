# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.GbE2.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
import noc.sa.script
from noc.sa.interfaces import IRemoveVlan

class Script(noc.sa.script.Script):
    name="HP.GbE2.remove_vlan"
    implements=[IRemoveVlan]
    def execute(self,vlan_id):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.configure():
            self.cli("/c/l2/vlan %d/del\ny\n"%vlan_id)
        self.save_config()
        return True
