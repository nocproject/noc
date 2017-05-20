# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT7500.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8700.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("show system")
        platform = ""
        version = ""

        for l in v.splitlines():
            l = l.split()
            if not l:
                continue
            if "Base" in l[0]:
                platform = l[2]
                rev = l[4]
                serial = l[5]
            if "Software" in l[0]:
                version = l[2].strip()

        return {
            "vendor": "Allied Telesis",
            "platform": platform,
            "version": version,
        }
