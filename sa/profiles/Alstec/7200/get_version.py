# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.7200.get_version
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
    name = "Alstec.7200.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^Machine Type\.+ (?:ALS24|VDSL2-24).+\n"
        r"^\s+(?:\S+\s+)?GE/Stack\s*\n"
        r"^Burned In MAC Address\.+ (?P<mac>\S+)\s*\n"
        r"^Software Version\.+ (?P<version>\S+)\s*\n"
        r"(^Bootloader Version\.+ (?P<bootprom>\S+)\s*\n)?",
        re.MULTILINE)

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        r = {
            "vendor": "Alstec",
            "platform": "7200",
            "version": match.group("version")
        }
        if match.group("bootprom"):
            r["attributes"] = {}
            r["attributes"]["Boot PROM"] = match.group("bootprom")

        return r
