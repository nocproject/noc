# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
    #Some versions of Mikrotik return parameter values in quotes
    rx_ver = re.compile(
        r"version: (?P<q>\"?)(?P<version>\d+\.\d+(\.\d+)?)(?P=q).+board-name: (?P<qp>\"?)(?P<platform>\D+?.\S+?)(?P=qp)\n",
        re.MULTILINE | re.DOTALL)
    rx_rb = re.compile(
        r"serial-number: (?P<qs>\"?)(?P<serial>\S+?)(?P=qs)\n.+current-firmware: "
        r"(?P<qb>\"?)(?P<boot>\d+\.\d+)(?P=qb)", re.MULTILINE | re.DOTALL)
=======
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(
        r"version: (?P<version>\d+\.\d+).+board-name: (?P<platform>\D+.\S+)",
        re.MULTILINE | re.DOTALL)
    rx_rb = re.compile(
        r"serial-number: (?P<serial>\S+).+current-firmware: "
        r"(?P<boot>\d+\.\d+)", re.MULTILINE | re.DOTALL)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        v = self.cli("system resource print")
        match = self.re_search(self.rx_ver, v)
        r = {
            "vendor": "MikroTik",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
<<<<<<< HEAD
        if r["platform"] not in ["x86", "CHR"]:
=======
        if r["platform"] != "x86":
            v = self.cli("system routerboard print")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            v = self.cli("system routerboard print")
            rb = self.re_search(self.rx_rb, v)
            if rb:
                r.update({"attributes": {}})
                r["attributes"].update({"Serial Number": rb.group("serial")})
                r["attributes"].update({"Boot PROM": rb.group("boot")})
        return r
