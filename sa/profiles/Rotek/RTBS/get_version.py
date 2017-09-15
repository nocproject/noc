# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RTBS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Rotek.RTBS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        r = {"vendor": "Rotek",
             "platform": "",
             "version": ""
             }
        # Try SNMP first
        if self.has_snmp():
            try:
                line = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                platform = line.split(",")[0].strip()
                v = line.split(",")[1].strip()
                sres = v.split(".")
                sw = "%s.%s.%s" % (sres[0], sres[1], sres[2])
                r = {
                    "vendor": "Rotek",
                    "platform": platform,
                    "version": sw,
                }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        """
        try:
            c = self.cli("show software version", cached=True)
        except self.CLISyntaxError:
            c = self.cli("show software-version", cached=True)

        line = c.split(" ")
        res = line[2].split(".", 2)
        vendor = res[0]
        platform = res[1]
        sres = res[2].split(".")
        sw = sres[0] + "." + sres[1]
        return {
            "vendor": vendor,
            "platform": platform,
            "version": sw,
            }
        """
        return r
