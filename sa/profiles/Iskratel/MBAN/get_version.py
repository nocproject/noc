# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MBAN.get_version
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
    name = "Iskratel.MBAN.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^\s*CPU: IskraTEL SGN MPC8560\s*\n"
        r"^\s*VxWorks: \S+\s*\n"
        r"^\s*Kernel: WIND version \S+\s*\n"
        r"^\s*ADSL2PLUS over POTS GS firmware version:\s+(?P<version>\S+)\s*\n",
        re.MULTILINE)

    def execute(self):
        v = self.scripts.get_inventory()
        match = self.rx_ver.search(self.cli("show version"))
        r = {
            "vendor": "Iskratel",
            "platform": "SGN",
            "version": match.group("version")
        }
        if "serial" in v[0]:
            r["attributes"] = {}
            r["attributes"]["Serial Number"] = v[0]["serial"]
        return r
