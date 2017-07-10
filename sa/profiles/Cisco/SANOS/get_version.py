# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.SANOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_platform = re.compile(
    r"^Hardware\n\s+cisco\s+(?P<platform>MDS\s+\S+)", re.MULTILINE)
rx_version = re.compile(
    r"^Software\n\s+BIOS:\s+version\s+\S+\n\s+loader:\s+version\s+\S+\n"
    r"\s+kickstart:\s+version\s+\S+\n\s+system:\s+version\s+(?P<version>\S+)\n",
    re.MULTILINE | re.DOTALL)
rx_image = re.compile(
    r"system image file is:\s+bootflash:\/(?P<image>\S+)",
    re.MULTILINE | re.DOTALL)

class Script(BaseScript):
    name = "Cisco.SANOS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("show hardware")
        platform = rx_platform.search(v).group("platform")
        version = rx_version.search(v).group("version")
        image = rx_image.search(v).group("image")
        return {
            "vendor": "Cisco",
            "platform": platform,
            "version": version,
            "attributes": {
                "image": image,
            }
        }
