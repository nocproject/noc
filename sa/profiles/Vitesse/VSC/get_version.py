# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vitesse.VSC.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Vitesse.VSC.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^\s*Chipset ID\s+:\s+(?P<platform>\S+).*\n", re.MULTILINE)
    rx_version = re.compile(
        r"^\s*Software Version\s+: \S+ \(standalone\)( dev-build by)? (?P<version>.+)\n",
        re.MULTILINE,
    )

    def execute(self):
        v = self.cli("show version", cached=True)
        match1 = self.rx_platform.search(v)
        match2 = self.rx_version.search(v)
        return {
            "vendor": "Vitesse",
            "platform": match1.group("platform"),
            "version": match2.group("version"),
        }
