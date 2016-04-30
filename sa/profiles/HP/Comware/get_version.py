# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.Comware.get_version
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
    name = "HP.Comware.get_version"
    cache = True
    interface = IGetVersion

    rx_version_HP = re.compile(
        r"^Comware Software, Version (?P<version>.+)$", re.MULTILINE)
    rx_platform_HP = re.compile(
        r"^HP (?P<platform>.*?) Switch", re.MULTILINE)

    def execute(self):
        platform = "Comware"
        version = "Unknown"

        v = self.cli("display version")
        match = self.rx_version_HP.search(v)
        if match:
            version = match.group("version")
        match = self.rx_platform_HP.search(v)
        if match:
            platform = match.group("platform")

        return {
            "vendor": "HP",
            "platform": platform,
            "version": version
        }