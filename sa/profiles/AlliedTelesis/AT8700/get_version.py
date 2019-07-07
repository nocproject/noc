# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT7500.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "AlliedTelesis.AT8700.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("show system")
        platform = ""
        version = ""

        for line in v.splitlines():
            line = line.split()
            if not line:
                continue
            if "Base" in line[0]:
                platform = line[2]
            if "Software" in line[0]:
                version = line[2].strip()

        return {"vendor": "Allied Telesis", "platform": platform, "version": version}
