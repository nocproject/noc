# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RT-BS.get_version
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
    name = "Rotek.RT-BS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
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
