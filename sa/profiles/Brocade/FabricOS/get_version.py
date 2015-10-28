# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.FabricOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_version = re.compile(r"Fabric OS:\s+v?(?P<version>\S+)", re.MULTILINE)
rx_platform = re.compile(r"^Part Num:\s+(?P<platform>\S+)", re.MULTILINE)


class Script(BaseScript):
    name = "Brocade.FabricOS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("version")
        vm = rx_version.search(v)
        v = self.cli("chassisshow")
        cm = rx_platform.search(v)
        return {
            "vendor": "Brocade",
            "platform": cm.group("platform"),
            "version": vm.group("version")
        }
