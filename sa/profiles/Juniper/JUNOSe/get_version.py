# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
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
    name = "Juniper.JUNOSe.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Juniper\s+(Edge Routing Switch )?(?P<platform>.+?)$.+"
        r"Version\s+(?P<version>.+?)\s*\[BuildId (?P<build>\d+)",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show version")
        match = self.re_search(self.rx_ver, v.replace(":", ""))
        return {
            "vendor": "Juniper",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Build": match.group("build"),
            }
        }
