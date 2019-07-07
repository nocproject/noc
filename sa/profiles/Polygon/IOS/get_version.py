# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Polygon.IOS.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Polygon.IOS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^(?P<platform>\S+\s\S+)\n.+,\s(?:Version:)?\s(?P<version>\S+\s\S+).+\n.+\n.+\n(?:System image file is)"
        r"?\s(?P<image><.+>)",
        re.MULTILINE,
    )
    rx_bootrom = re.compile(r"(?:[Bb]ootrom\s[Vv]ersion\s:)\s\s(?P<bootrom>\S+)")

    def execute_cli(self, **kwargs):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        match1 = self.re_search(self.rx_bootrom, v)
        platform = match.group("platform")
        bootrom = match1.group("bootrom")
        s = (
            self.snmp.get(mib["1.3.6.1.4.1.14885.1001.6004.1.3.1.11.0.0.1"])
            if self.has_snmp()
            else None
        )
        r = {
            "vendor": "Polygon",
            "platform": platform,
            "version": match.group("version"),
            "attributes": {"image": match.group("image")},
        }
        if bootrom:
            r["attributes"]["Boot PROM"] = bootrom
        if s:
            r["attributes"]["Serial Number"] = s
        return r
