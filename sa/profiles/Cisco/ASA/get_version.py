# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.ASA.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Cisco.ASA.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Cisco (?:Adaptive|PIX) Security Appliance Software Version (?P<version>\S+)"
        r".+Hardware:\s+(?P<platform>.+?),",
        re.MULTILINE | re.DOTALL
    )
    rx_image = re.compile(
        r".+System image file is \".+?:/(?P<image>.+?)\"",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        if self.capabilities.get("Cisco | ASA | Security | Context | Mode"):
            if self.capabilities["Cisco | ASA | Security | Context | Mode"] == "multiple":
                self.cli("changeto system")

        v = self.cli("show version")
        match = self.re_search(self.rx_ver, v)
        try:
            image = self.re_search(self.rx_image, v).group("image")
        except self.UnexpectedResultError:
            image = ""
        return {
            "vendor": "Cisco",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "image": image,
            }
        }
