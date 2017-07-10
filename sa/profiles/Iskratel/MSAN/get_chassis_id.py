# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MSAN.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Iskratel.MSAN.get_chassis_id"
    interface = IGetChassisID
    cache = True

    def execute(self):
        v = self.profile.get_hardware(self)
        return {
            "first_chassis_mac": v["mac"],
            "last_chassis_mac": v["mac"]
        }
