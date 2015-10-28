# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
from __future__ import with_statement
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IRemoveVlan


class Script(BaseScript):
    name = "Zyxel.ZyNOS.remove_vlan"
    interface = IRemoveVlan

    def execute(self, vlan_id):
        for v in  self.scripts.get_vlans():
            if v["vlan_id"] == vlan_id:
                with self.configure():
                    self.cli("no vlan %s" % v["vlan_id"])
                self.save_config()
                return True
        return False
