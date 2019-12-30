# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.SwOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "MikroTik.SwOS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        r = {}
        sys_info = self.profile.parseBrokenJson(self.http.get("/sys.b", cached=True, eof_mark="}"))
        r = {
            "vendor": "MikroTik",
            "platform": sys_info["brd"].decode("hex"),
            "version": sys_info["ver"].decode("hex"),
            "attributes": {"Serial Number": sys_info["sid"].decode("hex")},
        }
        return r
