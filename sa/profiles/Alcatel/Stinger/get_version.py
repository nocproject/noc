# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.Stinger.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alcatel.Stinger.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Software version (?P<version>\S+)\n\n"
        r"Hardware revision:\s(?P<revision>\S+)\s*(?P<platform>\S+).+",
        re.MULTILINE | re.IGNORECASE,
    )

    def execute(self):
        v = self.cli("version")
        match = self.rx_ver.search(v)
        if not match:
            raise self.UnexpectedResultError()
        return {
            "vendor": "Alcatel",
            "version": match.group("version"),
            "platform": match.group("platform"),
            "revision": match.group("revision"),
        }
