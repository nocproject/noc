# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.ihasvlan import IHasVlan, IGetVlans
import re


class Script(BaseScript):
    name = "Generic.has_vlan"
    interface = IHasVlan
    requires = [("get_vlans", IGetVlans)]

    def execute(self, vlan_id):
        for v in self.scripts.get_vlans():
            if v["vlan_id"] == vlan_id:
                return True
        return False
