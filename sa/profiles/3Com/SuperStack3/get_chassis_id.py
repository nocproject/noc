# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "3Com.SuperStack3.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self):
        v = self.profile.get_hardware(self)
        return {
            "first_chassis_mac": v["mac"],
            "last_chassis_mac": v["mac"]
        }
