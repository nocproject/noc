# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dell.Powerconnect62xx.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IRemoveVlan


class Script(BaseScript):
    name = "Dell.Powerconnect62xx.remove_vlan"
    interface = IRemoveVlan

    def execute(self, vlan_id):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.configure():
            self.cli("vlan database")
            self.cli("no vlan %d" % vlan_id)
        self.save_config()
        return True
