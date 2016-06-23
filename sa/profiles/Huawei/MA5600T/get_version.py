# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.MA5600T.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Huawei.MA5600T.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(
        r"^\s*(?P<platform>MA\S+)(?P<version>V\S+)\s+RELEASE SOFTWARE",
        re.MULTILINE)

    def execute(self):
        v = self.cli("display version\n")
        match = self.re_search(self.rx_ver, v)
        r = {
            "vendor": "Huawei",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
        return r
