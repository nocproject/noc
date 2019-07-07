# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTE.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Eltex.LTE.get_version"
    interface = IGetVersion
    cache = True

    rx_version = re.compile(r"^Eltex LTE software version\s+(?P<version>\S+\s+build\s+\d+)")
    rx_hw = re.compile(
        r"^Device type:\s+(?P<platform>\S+)\s*\n" r"^Serial number:\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_version.search(v)
        version = match.group("version")
        r = {"vendor": "Eltex", "platform": "LTE", "version": version}
        try:
            v = self.cli("show factory settings", cached=True)
            match = self.rx_hw.search(v)
            r["platform"] = match.group("platform")
            r["attributes"] = {}
            r["attributes"]["Serial Number"] = match.group("serial")
        except self.CLISyntaxError:
            pass

        return r
