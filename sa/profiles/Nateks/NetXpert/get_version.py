# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Nateks.NetXpert.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Nateks.NetXpert.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r".*Series Software, Version (?P<version>[\S\s]*)\, RELEASE SOFTWARE", re.MULTILINE
    )
    rx_boot = re.compile(
        r".*ROM: System Bootstrap, Version (?P<bootrom>\d+\.\d+\.\d+).*", re.MULTILINE
    )
    rx_sn = re.compile(r"Serial num:(?P<sn>[^ ,]+),.*\n", re.MULTILINE)
    rx_plat = re.compile(r"Nateks (?P<platform>.*) RISC", re.MULTILINE)

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        version = match.group("version")
        match = self.rx_boot.search(v)
        bootrom = match.group("bootrom")
        match = self.rx_sn.search(v)
        sn = match.group("sn")
        match = self.rx_plat.search(v)
        platform = match.group("platform")

        return {
            "vendor": "Nateks",
            "platform": platform,
            "version": version,
            "attributes": {"Boot PROM": bootrom, "Serial Number": sn},
        }
