# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.Comware.get_version
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
    name = "HP.Comware.get_version"
    cache = True
    interface = IGetVersion

    rx_version_HP = re.compile(
        r"^Comware Software, Version (?P<version>.+)$", re.MULTILINE)
    rx_platform_HP = re.compile(
        r"^HP (?P<platform>.*?) Switch", re.MULTILINE)
    rx_devinfo = re.compile(
        r"^Slot 1:\nDEVICE_NAME\s+:\s+(?P<platform>\S+)\s+.+?\n"
        r"DEVICE_SERIAL_NUMBER\s+:\s+(?P<serial>\S+)\n")

    def execute(self):
        platform = "Comware"
        version = "Unknown"

        v = self.cli("display version")
        match = self.rx_version_HP.search(v)
        if match:
            version = match.group("version")
        match = self.rx_platform_HP.search(v)
        if match:
            platform = match.group("platform")
        if platform == "Comware":
            try:
                v = self.cli("display device manuinfo")
                match = self.rx_devinfo.search(v)
                if match:
                    platform = match.group("platform")
            except:
                pass

        return {
            "vendor": "HP",
            "platform": platform,
            "version": version
        }
