# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.ihasvlan import IHasVlan
from noc.sa.interfaces.igetvlans import IGetVlans

import re


<<<<<<< HEAD
class Script(BaseScript):
    name = "Generic.has_vlan"
    interface = IHasVlan
    requires = ["get_vlans"]
=======
class Script(noc.sa.script.Script):
    name = "Generic.has_vlan"
    implements = [IHasVlan]
    requires = [("get_vlans", IGetVlans)]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self, vlan_id):
        for v in self.scripts.get_vlans():
            if v["vlan_id"] == vlan_id:
                return True
        return False
