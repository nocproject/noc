# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# BDCOM.xPON.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "BDCOM.xPON.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"BDCOM\S+\s+(?P<platform>\S+)\s+\S+\s+Version\s+(?P<version>\S+)\s"
        r"Build\s(?P<build>\d+).+System Bootstrap,\s*Version\s(?P<boot>\S+),"
        r"\s*Serial num:(?P<serial>\d+)",
        re.MULTILINE | re.DOTALL)

    rx_hver = re.compile(
        r"^hardware version:(?:V|)(?P<hversion>\S+)",
        re.MULTILINE)

    # todo: add hardware ver for P3310C, P3608 (snmp output need)

    def execute(self):
        if self.has_snmp():
            try:
                # sysDescr.0
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                if v:
                    match = self.re_search(self.rx_ver, v)
                    return {
                        "vendor": "BDCOM",
                        "platform": match.group("platform"),
                        "version": match.group("version"),
                        "attributes": {
                            "build": match.group("build"),
                            "boot": match.group("boot"),
                            "serial": match.group("serial")
                        }
                    }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show version")
        match = self.rx_ver.search(v)
        if match:
            return {
                "vendor": "BDCOM",
                "platform": match.group("platform"),
                "version": match.group("version"),
                "attributes": {
                    "build": match.group("build"),
                    "boot": match.group("boot"),
                    "serial": match.group("serial")
                }

            }
