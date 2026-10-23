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
    reuse_cli_session = False
    keep_cli_session = False

    rx_platform = re.compile(r"\|\|\s+0\s+\|\|\s+(?P<platform>.+)\s*\n")

    rx_ver = re.compile(
        r"^\s*NI CARD TYPE\s+: (?P<cardtype>.+)\n^\s*NI SW VERSION NAME\s+: (?P<version>.+)\n",
        re.MULTILINE,
    )

    def execute(self):
        match = self.rx_ver.search(self.cli("ver"))
        if not match:
            version = "None"
            cardtype = "None"
            platform = "None"
        else:
            version = match.group("version").strip()
            cardtype = match.group("cardtype").strip()
            c = self.cli("EXISTSH ALL")
            match = self.rx_platform.search(c)
            platform = match.group("platform")
        return {
            "vendor": "ECI",
            "platform": platform,
            "version": version,
            "attributes": {"cardtype": cardtype},
        }
