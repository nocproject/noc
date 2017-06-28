# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "3Com.SuperStack3.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.profile.get_hardware(self)
        return {
            "vendor": "3Com",
            "platform": v["platform"],
            "version": v["version"],
            "attributes": {
                "Boot PROM": v["bootprom"],
                "HW version": v["hardware"],
                "Serial Number": v["serial"]
            }
        }
