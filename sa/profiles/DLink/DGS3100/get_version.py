# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DGS3100.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "DLink.DGS3100.get_version"
    cache = True
    interface = IGetVersion
=======
##----------------------------------------------------------------------
## DLink.DGS3100.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re


class Script(noc.sa.script.Script):
    name = "DLink.DGS3100.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_ver = re.compile(
        r"Device Type\s+:\s+(?P<platform>\S+).+Boot PROM Version\s+:\s+"
        r"(?:Build\s+)?(?P<bootprom>\S+).+Firmware Version\s+:\s+"
        r"(?:Build\s+)?(?P<version>\S+).+Hardware Version\s+:\s+"
        r"(?P<hardware>\S+)", re.MULTILINE | re.DOTALL)
    rx_ser = re.compile(
        r"Serial Number\s+:\s+(?P<serial>.+)\nSystem Name",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        s = self.cli("show switch", cached=True)
        match = self.re_search(self.rx_ver, s)
<<<<<<< HEAD
        r = {
            "vendor": "DLink",
=======
        r = {"vendor": "DLink",
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware")
            }
        }
        ser = self.rx_ser.search(s)
<<<<<<< HEAD
        # Firmware 1.00.36 do not show serial number
        if ser:
            r["attributes"]["Serial Number"] = ser.group("serial")
=======
        r["attributes"].update({"Serial Number": ser.group("serial")})
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r
