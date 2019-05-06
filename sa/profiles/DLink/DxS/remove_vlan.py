# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.remove_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iremovevlan import IRemoveVlan


class Script(BaseScript):
    name = "DLink.DxS.remove_vlan"
    interface = IRemoveVlan

    def execute(self, vlan_id):
        for v in self.scripts.get_vlans():
            if v["vlan_id"] == vlan_id:
                with self.configure():
                    self.cli("delete vlan %s" % v["name"])
                self.save_config()
                return True
        return False
