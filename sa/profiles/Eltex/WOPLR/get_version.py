# ---------------------------------------------------------------------
# Eltex.WOPLR.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Eltex.WOPLR.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^\s*hw-platform\s*(\||:)\s*(?P<platform>.+)", re.MULTILINE)
    rx_version = re.compile(r"^\s*software-version\s*(\||:)\s*(?P<version>\S+)", re.MULTILINE)
    rx_sn = re.compile(r"^\s*factory-serial-number\s*(\||:)\s*(?P<sn>\S+)", re.MULTILINE)
    rx_hwversion = re.compile(r"^\s*hw-revision\s*(\||:)\s*(?P<hwversion>\S+)", re.MULTILINE)

    def execute_cli(self, **kwargs):
        c = self.cli("monitoring information", cached=True)

        match = self.rx_platform.search(c)
        platform = match.group("platform")

        match = self.rx_version.search(c)
        version = match.group("version")

        match = self.rx_sn.search(c)
        sn = match.group("sn")

        match = self.rx_hwversion.search(c)
        hwversion = match.group("hwversion")
        return {
            "vendor": "Eltex",
            "platform": platform,
            "version": version,
            "attributes": {"HW version": hwversion, "Serial Number": sn},
        }
