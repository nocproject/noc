# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ElectronR.KO01M.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "ElectronR.KO01M.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute_snmp(self):
        # Try SNMP first
        base = self.snmp.get("1.3.6.1.4.1.35419.1.1.6.0")
        if base:
            return [{
                "first_chassis_mac": base,
                "last_chassis_mac": base
            }]
