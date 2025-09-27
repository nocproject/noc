# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_version
# Izya12@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(r"^.*WANFleX\s+(?P<version>\S+).+SN:(?P<sn>\d+)", re.MULTILINE)
    rx_platform = re.compile(r"PN:(?P<platform>.+)\/(?P<hardware>.+)$", re.MULTILINE)

    def execute(self):
        v = self.cli("system version", cached=True)
        v_match = self.rx_ver.search(v)
        version = v_match.group("version")
        sn = v_match.group("sn")
        p_match = self.rx_platform.search(v)
        if p_match:
            platform = p_match.group("platform")
            hardware = p_match.group("hardware")
        else:
            lv = self.cli("license -show", cached=True)
            p_match2 = self.rx_platform.search(lv)
            if p_match2:
                platform = p_match2.group("platform")
                hardware = p_match2.group("hardware")
            else:
                platform = "Unknown"
                hardware = "Unknown"
        return {
            "vendor": "InfiNet",
            "platform": platform,
            "version": version,
            "attributes": {"HW version": hardware, "Serial Number": sn},
        }
