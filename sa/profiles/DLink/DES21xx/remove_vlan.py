# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DES21xx.remove_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iremovevlan import IRemoveVlan


class Script(BaseScript):
    name = "DLink.DES21xx.remove_vlan"
    interface = IRemoveVlan

    def execute(self, vlan_id):
        self.cli("delete vlan tag %d" % vlan_id)
        self.save_config()
        return True
