# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES3xxx.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
import noc.sa.script
from noc.sa.interfaces import IRemoveVlan

class Script(noc.sa.script.Script):
    name="DLink.DES3xxx.remove_vlan"
    implements=[IRemoveVlan]
    def execute(self,vlan_id):
        for v in  self.scripts.get_vlans():
            if v["vlan_id"]==vlan_id:
                with self.configure():
                    self.cli("delete vlan %s"%v["name"])
                self.save_config()
                return True
        return False