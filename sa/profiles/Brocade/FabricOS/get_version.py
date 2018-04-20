# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Brocade.FabricOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re

rx_version = re.compile(r"Fabric OS:\s+v?(?P<version>\S+)", re.MULTILINE)
rx_platform = re.compile(r"^Part Num:\s+(?P<platform>\S+)", re.MULTILINE)


<<<<<<< HEAD
class Script(BaseScript):
    name = "Brocade.FabricOS.get_version"
    cache = True
    interface = IGetVersion
=======
class Script(noc.sa.script.Script):
    name = "Brocade.FabricOS.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
