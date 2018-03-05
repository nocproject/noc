# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MBAN.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Iskratel.MBAN.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^\s*CPU: IskraTEL (?P<platform>\S+) .+\n"
        r"^\s*VxWorks: \S+\s*\n"
        r"^\s*Kernel: WIND version \S+\s*\n"
        r"^\s*ADSL(?:2PLUS)? over (?:POTS|ISDN) GS firmware version:\s+(?P<version>\S+)\s*\n",
        re.MULTILINE)
    rx_inv1 = re.compile(
        r"^\s*(?P<number>\d+)\s+\S+\s+\S+\s+(?P<part_no>U\S+)\s+"
        r"(?P<serial>[NZ]\S+)\s+", re.MULTILINE)
    rx_inv2 = re.compile(
        r"^\s*(?P<number>\d+)\s+\S+\s+(?P<part_no>U\S+)\s+[UN]\S+\s+"
        r"(?P<serial>[0-9A-Z\/]+)\s+", re.MULTILINE)

    def execute(self):
        c = self.cli("show version", cached=True)
        match = self.rx_ver.search(c)
        r = {
            "vendor": "Iskratel",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
        c = self.cli("show board", cached=True)
        match = self.rx_inv1.search(c)
        if not match:
            match = self.rx_inv2.search(c)
        if match.group("serial") != "N/A":
            r["attributes"] = {}
            r["attributes"]["Serial Number"] = match.group("serial")
        return r
