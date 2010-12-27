# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES2108.remove_vlan
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
    name="DLink.DES2108.remove_vlan"
    implements=[IRemoveVlan]
    def execute(self,vlan_id):
        self.cli("delete vlan tag %d"%vlan_id)
        self.save_config()
        return True
