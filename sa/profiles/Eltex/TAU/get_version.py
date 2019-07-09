# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.TAU.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
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
    name = "Eltex.TAU.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^(?P<platform>\S.+)\n"
        r"System version:\s+#(?P<sysver>\S+)\n"
        r"\S.+\nFirmware\sversion:\s+(?P<fwver>\S+)",
        re.MULTILINE,
    )

    def execute(self):
        c = self.cli("system info")
        match = self.rx_ver.search(c)
        if match:
            platform = match.group("platform")
            fwversion = match.group("fwver")
            version = match.group("sysver")
        else:
            platform = "None"
            fwversion = "None"
            version = "None"

        return {
            "vendor": "Eltex",
            "platform": platform,
            "version": version,
            "attributes": {"FW version": fwversion},
        }
