# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Raisecom.RCIOS.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Raisecom.RCIOS.get_version"
    interface = IGetVersion
    cache = True

    def execute(self):
        r = []
        v = self.cli("show version", cached=True)
        for line in v.splitlines():
            r = line.split(':', 1)
            if r[0].strip() == "Version":
                version = r[1].strip()
            if r[0].strip() == "Device":
                platform = r[1].strip()
            if r[0].strip() == "Serial number":
                serial = r[1].strip()
            if r[0].strip() == "IOS version":
                hw_rev = r[1].strip()
            if r[0].strip() == "Bootrom version":
                bootstrap = r[1].strip()
        return {
            "vendor": "Raisecom",
            "platform": platform,
            "version": version,
            "attributes": {
                "Serial Number": serial,
                "Boot PROM": bootstrap,
                "HW version": hw_rev
            }
        }
