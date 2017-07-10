# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTE.remove_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iremovevlan import IRemoveVlan


class Script(BaseScript):
    name = "Eltex.LTE.remove_vlan"
    interface = IRemoveVlan

    def execute(self, vlan_id):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.profile.switch(self):
            self.cli("configure")
            self.cli("no vlan %d" % vlan_id)
            self.cli("exit")
        self.save_config()
        return True
