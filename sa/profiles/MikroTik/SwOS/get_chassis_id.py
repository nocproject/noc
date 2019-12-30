# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.SwOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "MikroTik.SwOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self):
        sys_info = self.profile.parseBrokenJson(self.http.get("/sys.b", cached=True, eof_mark="}"))
        return {"first_chassis_mac": sys_info["mac"], "last_chassis_mac": sys_info["mac"]}
