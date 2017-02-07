# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.MA5300.get_version
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

class Script(BaseScript):
    name = "Huawei.MA5300.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"SmartAX (?P<platform>\S+) (?P<version>\S+)")

    def execute(self):
        self.cli("en")
        hostname = self.scripts.get_fqdn()
        v = self.cli("show version")
        match = self.re_search(self.rx_ver, v)
        r = {
            "vendor": "Huawei",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "hostname" : hostname
        }
        return r

