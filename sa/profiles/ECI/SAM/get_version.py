# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ECI.SAM.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "ECI.SAM.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"\|\|\s+0\s+\|\|\s+(?P<platform>.+)\s*\n")

    rx_ver = re.compile(
        r"^\s*NI CARD TYPE\s+: (?P<cardtype>.+)\n"
        r"^\s*NI SW VERSION NAME\s+: (?P<version>.+)\n",
        re.MULTILINE
    )

    def execute(self):
        match = self.rx_ver.search(self.cli("ver"))
        version = match.group("version")
        cardtype = match.group("cardtype")
        if "IPNI" in cardtype:
            with self.profile.shell(self):
                self.cli("SHELF")
                c = self.cli("EXISTSH 0 ")
                self.cli("END")
                match = self.rx_platform.search(c)
                platform = match.group("platform")
        elif "SANI" in cardtype:
            c = self.cli("EXISTSH 0 ")
            match = self.rx_platform.search(c)
            platform = match.group("platform")
        return {
            "vendor": "ECI",
            "platform": platform,
            "version": version,
            "attributes": {
                "cardtype": cardtype
            }
        }