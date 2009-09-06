# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.remove_vlan
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
    name="Force10.FTOS.remove_vlan"
    implements=[IRemoveVlan]
    def execute(self,vlan_id):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.configure():
            self.cli("no interface vlan %d"%vlan_id)
        self.save_config()
        return True
