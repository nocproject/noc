# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Sumavision.EMR.get_version
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
    name = "Sumavision.EMR.get_version"
    interface = IGetVersion

    rx_ver = re.compile(r"VID_WEB_VER = \"(?P<ver>.*?)\"", re.DOTALL | re.MULTILINE)

    def execute(self):
        data = self.http.get("/en/version_info.asp", use_basic=True)
        match = self.rx_ver.search(data)
        if not match:
            raise self.UnexpectedResultError()
        version = match.group("ver")
        return {
            "vendor": "Sumavision",
            "platform": "EMR",
            "version": version if version else "Unknown",
        }
