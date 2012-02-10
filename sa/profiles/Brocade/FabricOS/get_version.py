# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.FabricOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_version = re.compile(r"Fabric OS:\s+v?(?P<version>\S+)", re.MULTILINE)
rx_platform = re.compile(r"^Part Num:\s+(?P<platform>\S+)", re.MULTILINE)


class Script(noc.sa.script.Script):
    name = "Brocade.FabricOS.get_version"
    cache = True
    implements = [IGetVersion]

    def execute(self):
        v = self.cli("version")
        vm = rx_version.search(v)
        v = self.cli("chassisshow")
        print v
        cm = rx_platform.search(v)
        return {
            "vendor": "Brocade",
            "platform": cm.group("platform"),
            "version": vm.group("version")
        }
