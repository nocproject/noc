# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raisecom.ROS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_ver = re.compile(r"^Product name:\s+(?P<platform>\S+).*ROS  Version ROS_(?P<version>.+?)\.\(Compiled", re.MULTILINE | re.DOTALL)


class Script(BaseScript):
    name = "Raisecom.ROS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("show version")
        match = rx_ver.search(v)
        return {
            "vendor": "Raisecom",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
