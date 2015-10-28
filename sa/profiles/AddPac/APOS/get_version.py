# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AddPac.APOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_ver = re.compile(
    r"(?P<platform>\S+) System software Revision (?P<version>\S+)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE)


class Script(BaseScript):
    name = "AddPac.APOS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("show version")
        match = rx_ver.search(v)
        return {
            "vendor": "AddPac",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
