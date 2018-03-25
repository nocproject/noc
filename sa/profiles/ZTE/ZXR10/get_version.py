# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXR10.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# re modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "ZTE.ZXR10.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^(?P<platform>.+?) Software, Version.*? (?P<version>\S+),.+ ROS Version (?P<ros>[^,].+?)System",
        re.MULTILINE | re.DOTALL)
    rx_snmp_ver1 = re.compile(
        r"ROS Version (?P<ros>.+?) (?P<platform>.+?) Software, Version.*? (?P<version>\S+), Copyright")
    rx_snmp_ver2 = re.compile(
        r"ZTE Ethernet Switch\s+(?P<platform>.+?), Version: (?P<version>\S+)")

    def execute_snmp(self):
        v = self.snmp.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
        match = self.rx_snmp_ver1.search(v)
        if not match:
            match = self.rx_snmp_ver2.search(v)
        platform = match.group("platform")
        if platform.startswith("ZXR10 "):
            platform = platform[6:]
        return {
            "vendor": "ZTE",
            "platform": platform,
            "version": match.group("version")
        }

    def execute_cli(self):
        v = self.cli("show version software")
        match = self.rx_ver.search(v)
        platform = match.group("platform")
        if platform.startswith("ZXR10 "):
            platform = platform[6:]
        return {
            "vendor": "ZTE",
            "platform": platform,
            "version": match.group("version")
        }
