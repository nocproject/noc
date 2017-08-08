# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DAS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "DLink.DAS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^Object-id\s+: (?P<sys_oid>\S+)\s*\n"
        r"^Up Time\(HH:MM:SS\)\s+: .+\n"
        r"^HwVersion\s+: (?P<hardware>\S+)\s*\n"
        r"^CPLDVersion\s+: .+\n"
        r"^CPSwVersion\s+: .+\n"
        r"^CPSwVersion\(Build\): (?P<version>\S+)",
        re.MULTILINE
    )

    OID_TABLE = {
        "1.3.6.1.4.1.171.10.65.1": "DAS-32xx"
    }

    def execute(self):
        v = self.cli("get system info")
        match = self.rx_ver.search(v)
        r = {
            "vendor": "DLink",
            "platform": self.OID_TABLE[match.group("sys_oid")],
            "version": match.group("version"),
            "attributes": {
                "HW version": match.group("hardware"),
            }
        }
        return r
