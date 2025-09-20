# ---------------------------------------------------------------------
# DLink.DxS.get_license
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modiles
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlicense import IGetLicense


class Script(BaseScript):
    name = "DLink.DxS.get_license"
    cache = True
    interface = IGetLicense
    rx_lic = re.compile(r"Device Default License : (?P<license>\S+)", re.MULTILINE)

    def execute_cli(self):
        try:
            c = self.cli("show dlms license")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        match = self.re_search(self.rx_lic, c)
        return {"license": match.group("license")}
