# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_license
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
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
    name = "DLink.DxS.get_license"
    cache = True
    implements = [IGetLicense]
    rx_lic = re.compile(r"Device Default License : (?P<license>\S+)",
        re.MULTILINE)

    def execute(self):
        try:
            c = self.cli("show dlms license")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        match = self.re_search(self.rx_lic, c)
        return {"license": match.group("license")}
