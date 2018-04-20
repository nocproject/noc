# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Raisecom.ROS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Raisecom.ROS.get_version"
    interface = IGetVersion
    cache = True

    def execute(self):
        v = self.profile.get_version(self)
        return {
            "vendor": "Raisecom",
            "platform": v["platform"],
            "version": v["version"],
            "attributes": {
                "Serial Number": v["serial"],
                "Boot PROM": v["bootstrap"],
                "HW version": v["hw_rev"]
            }
=======
##----------------------------------------------------------------------
## Raisecom.ROS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver = re.compile(r"^Product name:\s+(?P<platform>\S+).*ROS  Version ROS_(?P<version>.+?)\.\(Compiled", re.MULTILINE | re.DOTALL)


class Script(noc.sa.script.Script):
    name = "Raisecom.ROS.get_version"
    cache = True
    implements = [IGetVersion]

    def execute(self):
        v = self.cli("show version")
        match = rx_ver.search(v)
        return {
            "vendor": "Raisecom",
            "platform": match.group("platform"),
            "version": match.group("version")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        }
