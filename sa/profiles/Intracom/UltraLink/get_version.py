# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Intracom.UltraLink.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Puthon modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Intracom.UltraLink.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"^\s+System Version\s:\s(?P<version>\S+)$", re.MULTILINE)
    rx_plat = re.compile(r"^\s+Board Model\s:\s(?P<platform>\S+)$", re.MULTILINE)

    def execute_cli(self, **kwargs):
        cmd = self.cli("get system info")
        ver = self.rx_ver.search(cmd)
        plat = self.rx_plat.search(cmd)
        return {
            "vendor": "Intracom",
            "platform": plat.group("platform"),
            "version": ver.group("version"),
        }
