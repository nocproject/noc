# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.MXK.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Zhone.MXK.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute_cli(self):
        return []
