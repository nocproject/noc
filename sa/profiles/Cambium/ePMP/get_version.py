# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cambium.ePMP.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Cambium.ePMP.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile(r"^\S+\.v(?P<version>[^@]+)$")

    def execute_cli(self):
        # Replace # with @ to prevent prompt matching
        r = {}
        v = self.cli("show dashboard", cached=True).strip()
        ee = [l.strip().split(" ", 1) for l in v.splitlines()]
        for e in ee:
            if len(e) == 2:
                r[e[0]] = e[1].strip()
            else:
                r[e[0]] = None

        return {
            "vendor": "Cambium",
            "platform": "ePMP1000",
            "version": r["cambiumCurrentuImageVersion"],
            "attributes": {
                "Boot PROM": r["cambiumUbootVersion"],
                "Serial Number": r["cambiumEPMPMSN"],
            },
        }
