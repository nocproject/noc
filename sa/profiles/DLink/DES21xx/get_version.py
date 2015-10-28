# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES21xx.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "DLink.DES21xx.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(r"Product Name:(?P<platform>\S+).+Firmware Version:(?P<version>\S+)", re.MULTILINE | re.DOTALL)

    def execute(self):
        match = self.re_search(self.rx_ver, self.cli("show switch"))
        return {
            "vendor": "DLink",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
