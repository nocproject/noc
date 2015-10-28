# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_ver = re.compile(
    r"ProductCode (?P<version>\S+) build.*Hardware type: (?P<platform>\S+)",
    re.MULTILINE | re.DOTALL)


class Script(BaseScript):
    name = "Protei.MediaGateway.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("_version full")
        match = rx_ver.search(v)
        return {
            "vendor": "Protei",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
