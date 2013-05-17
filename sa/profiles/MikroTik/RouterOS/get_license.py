# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_license
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modiles
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLicense


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_license"
    cache = True
    implements = [IGetLicense]
    rx_lic = re.compile(
        r"^\s*software-id: (?P<sid>\S+).+upgradable-to: (?P<upto>\S+).+nlevel:"
        r" (?P<nlevel>\d+).+features:.*(?P<features>\.*)$",
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
