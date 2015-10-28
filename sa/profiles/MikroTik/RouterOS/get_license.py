# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_license
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modiles
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlicense import IGetLicense


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_license"
    cache = True
    interface = IGetLicense
    rx_lic = re.compile(
        r"^\s*software-id: (?P<sid>\S+)\n"
        r"(^\s*upgradable-to: (?P<upto>\S+)\n)?"
        r"^\s*nlevel: (?P<nlevel>\d+)\n"
        r"(^\s*features:.*(?P<features>\.*)$)?",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("system license print")
        match = self.re_search(self.rx_lic, v)
        r = {
            "software-id": match.group("sid"),
            "upgradable-to": match.group("upto"),
            "nlevel": int(match.group("nlevel")),
        }
        features = match.group("features").strip()
        if features:
            r.update({"features": features})
        return r
