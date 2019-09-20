# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Upvel.UP.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Upvel.UP.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^\s*Model Name\s+: (?P<platform>\S+).*\n", re.MULTILINE)
    rx_version = re.compile(
        r"^\s*Software Version\s+: \S+ \(standalone\)( dev-build by)? (?P<version>.+)\n",
        re.MULTILINE,
    )
    rx_image = re.compile(r"^\s*Image\s+: (?P<image>\S+.dat)", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        r = {
            "vendor": "Upvel",
            "platform": self.rx_platform.search(v).group("platform"),
            "version": self.rx_version.search(v).group("version"),
        }
        match = self.rx_image.search(v)
        if match:
            r["image"] = match.group("image")
        return r
