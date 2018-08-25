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

    rx_descr = re.compile(r"Description\s+: (?P<platform>\S+)")
    rx_ver = re.compile(
        r"^Object-id\s+: (?P<sys_oid>\S+)\s*\n"
        r"^Up Time\(HH:MM:SS\)\s+: .+\n"
        r"^HwVersion\s+:(?P<hardware>.*)\n"
        r"(^CPLDVersion\s+: .+\n)?"
        r"^CPSwVersion\s+: .+\n"
        r"^CPSwVersion\(Build\): (?P<version>\S+).*\n"
        r"^DPSwVersion\s+: .+\n",
        re.MULTILINE
    )
    rx_ver2 = re.compile(
        r"^Object-id\s+: (?P<sys_oid>\S+)\s*\n"
        r"^Up Time\(HH:MM:SS\)\s+: .+\n"
        r"^HwVersion\s+:(?P<hardware>.*)\n"
        r"^CPSwVersion\s+: (?P<version>\S+)\s*\n"
        r"^DPSwVersion\s+: .+",
        re.MULTILINE
    )
    OID_TABLE = {
        "1.3.6.1.4.1.171.10.65.1": "DAS-32xx",
        "1.3.6.1.4.1.3278.1.12": "DAS-3248",
        "1.3.6.1.4.1.3646.1300.11": "DAS-3248DC",
        "1.3.6.1.4.1.3646.1300.12": "DAS-3248",
        "1.3.6.1.4.1.3646.1300.13": "DAS-3224DC",
        "1.3.6.1.4.1.3646.1300.14": "DAS-3224",
        "1.3.6.1.4.1.3646.1300.15": "DAS-3216DC",
        "1.3.6.1.4.1.3646.1300.16": "DAS-3216",
        "1.3.6.1.4.1.3646.1300.19": "DAS-3248/E",
        "1.3.6.1.4.1.3646.1300.202": "DAS-3224/E",
    }

    def execute(self):
        v = self.cli("get system info")
        match = self.rx_descr.search(v)
        platform = match.group("platform")
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver2.search(v)
        if not platform.startswith("DAS-"):
            platform = self.OID_TABLE[match.group("sys_oid")]
        r = {
            "vendor": "DLink",
            "platform": platform,
            "version": match.group("version"),
        }
        if (
            match.group("hardware") and
            match.group("hardware").strip()
        ):
            r["attributes"] = {}
            r["attributes"]["HW version"] = match.group("hardware").strip()
        return r
