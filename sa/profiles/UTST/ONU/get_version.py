# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# UTST.OMN.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "UTST.ONU.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^sysName\s+:\s(?P<platform>\S+)?",
        re.MULTILINE)

    rx_ver = re.compile(
        r"SW\s+software\sVer\s:\s(?P<version>\S+)?",
        re.MULTILINE)
    rx_ver2 = re.compile(
        r"^(?P<version>\S+\s\S+\s\S+)",
        re.MULTILINE)

    def execute(self):
        cmd = self.cli("show system")
        match = self.rx_platform.search(cmd)
        if not match:
            platform = "ONU2004"
        else:
            platform = match.group("platform")
        vcmd = self.cli("show version")
        match = self.rx_ver.search(vcmd)
        if not match:
            match = self.rx_ver2.search(vcmd)
        version = match.group("version")
        return {
            "vendor": "UTST",
            "platform": platform,
            "version": version
            }