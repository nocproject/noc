# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXR10.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
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

    rx_ver = re.compile(r"^(?P<platform>.+?) Software, Version (?P<version>[^,]+).+ ROS Version (?P<ros>[^,].+?)System", re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(r"ROS Version (?P<ros>.+?) (?P<platform>.+?) Software, Version (?P<version>[^,]+) Copyright")

    def execute(self):
        if self.has_snmp():
            try:
                v = self.snmp.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
                match = self.rx_snmp_ver.search(v)
                return {
                    "vendor": "ZTE",
                    "platform": match.group("platform"),
                    "version": match.group("version")
                }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show version software")
        match = self.rx_ver.search(v)
        return {
            "vendor": "ZTE",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
