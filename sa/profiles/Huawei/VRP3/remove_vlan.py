# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.remove_vlan
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IRemoveVlan


class Script(BaseScript):
    name = "Huawei.VRP3.remove_vlan"
    interface = IRemoveVlan

    def execute(self, vlan_id):
        for v in self.scripts.get_vlans():
            if v["vlan_id"] == vlan_id:
                with self.configure():
                    self.cli("interface lan 0/0 \n")
                    self.cli("no vlan vlanId %d" % v["vlan_id"])
                self.save_config()
                return True
        return False
