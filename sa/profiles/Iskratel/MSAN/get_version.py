# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Iskratel.MSAN.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Iskratel.MSAN.get_version"
    interface = IGetVersion
    cache = True

    def execute(self):
        v = self.profile.get_hardware(self)
        return {
            "vendor": "MSAN",
            "platform": v["platform"],
            "version": v["api_ver"],
            "attributes": {
                "Serial Number": v["serial"]
            }
        }
