# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5300.get_version
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Huawei.MA5300.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"SmartAX (?P<platform>\S+) \S+")
    rx_ver = re.compile(r"Version (?P<version>\S+)")

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        version = match.group("version")
        match = self.re_search(self.rx_platform, v)
        platform = match.group("platform")
        r = {
            "vendor": "Huawei",
            "platform": platform,
            "version": version
        }
        return r
