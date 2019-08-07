# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.WOPLR.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Eltex.WOPLR.get_version"
    cache = True
    interface = IGetVersion

    def execute_cli(self, **kwargs):
        c = self.cli("monitoring information", cached=True)
        for line in c.splitlines():
            r = line.split(":", 1)
            if r[0].strip() == "software-version":
                version = r[1].strip()
            if r[0].strip() == "hw-platform":
                platform = r[1].strip()
            if r[0].strip() == "factory-serial-number":
                sn = r[1].strip()
            if r[0].strip() == "hw-revision":
                hwversion = r[1].strip()
        return {
            "vendor": "Eltex",
            "platform": platform,
            "version": version,
            "attributes": {"HW version": hwversion, "Serial Number": sn},
        }
