# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_version
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
    name = "MikroTik.RouterOS.get_version"
    cache = True
    interface = IGetVersion
    # Some versions of Mikrotik return parameter values in quotes
    rx_ver = re.compile(
        r"version: (?P<q>\"?)(?P<version>\d+\.\d+(\.\d+)?)(?P=q).+board-name: (?P<qp>\"?)(?P<platform>\D+?.\S+?)(?P=qp)\n",
        re.MULTILINE | re.DOTALL)
    rx_rb = re.compile(
        r"serial-number: (?P<qs>\"?)(?P<serial>\S+?)(?P=qs)\n.+current-firmware: "
        r"(?P<qb>\"?)(?P<boot>\d+\.\d+)(?P=qb)", re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("system resource print")
        match = self.re_search(self.rx_ver, v)
        r = {
            "vendor": "MikroTik",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
        if r["platform"] not in ["x86", "CHR"]:
            v = self.cli("system routerboard print")
            rb = self.re_search(self.rx_rb, v)
            if rb:
                r.update({"attributes": {}})
                r["attributes"].update({"Serial Number": rb.group("serial")})
                r["attributes"].update({"Boot PROM": rb.group("boot")})
        return r
