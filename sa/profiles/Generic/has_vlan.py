# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IHasVlan, IGetVlans
import re

class Script(noc.sa.script.Script):
    name="Generic.has_vlan"
    implements=[IHasVlan]
    requires=[("get_vlans",IGetVlans)]
    def execute(self,vlan_id):
        for v in self.scripts.get_vlans():
            if v["vlan_id"]==vlan_id:
                return True
        return False
