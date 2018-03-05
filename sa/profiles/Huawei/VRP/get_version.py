# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Huawei.VRP.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^VRP.+Software, Version (?P<version>[^ ,]+),? .*?\n"
        r"\s*(?:Quidway|Huawei) (?P<platform>(?:NetEngine\s+|MultiserviceEngine\s+)?\S+)[^\n]+uptime",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    rx_ver_snmp = re.compile(
        r"Versatile Routing Platform Software.*?"
        r"Version (?P<version>[^ ,]+),? .*?\n"
        r"\s*(?:Quidway|Huawei) (?P<platform>(?:NetEngine\s+)?"
        r"[^ \t\n\r\f\v\-]+)[^\n]+",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    rx_ver_snmp2 = re.compile(
        r"(?P<platform>(?:\S+\s+)?(?:S\d+|AR\d+\S*)(?:[A-Z]+-[A-Z]+)?(?:\d+\S+)?)"
        r"\s+Huawei\sVersatile\sRouting\sPlatform"
        r"\sSoftware.*Version\s(?P<version>\d+\.\d+)\s"
        r"\((?:S\d+|AR\d+\S*)\s(?P<image>\S+)+\).*",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    rx_ver_snmp3 = re.compile(
        r"^\s*VRP.+Software, Version (?P<version>\S+)\s+"
        r"\((?P<platform>S\S+|CX\d+) (?P<image>[^)]+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    rx_ver_snmp4_ne_me = re.compile(
        r"Huawei Versatile Routing Platform Software.*?"
        r"Version (?P<version>\S+) .*?"
        r"\s*(?P<platform>NetEngine\s+|MultiserviceEngine\s+\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    rx_ver_snmp5 = re.compile(
        r"Huawei Versatile Routing Platform.*?"
        r"Version (?P<version>\S+) .*?"
        r"\s*(?:Quidway|Huawei) (?P<platform>[A-Z0-9]+)\s",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    rx_ver_snmp6 = re.compile(
        r"Huawei Versatile Routing Platform .* \((?P<platform>[A-Z0-9]+) (?P<version>\S+)\) .*?",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    BAD_PLATFORM = ["", "Quidway S5600-HI"]

    def execute(self):
        v = ""
        match_re_list = [
            self.rx_ver,
            self.rx_ver_snmp,
            self.rx_ver_snmp2,
            self.rx_ver_snmp3,
            self.rx_ver_snmp5
        ]
        if self.has_snmp():
            # Trying SNMP
            try:
                # SNMPv2-MIB::sysDescr.0
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
            except self.snmp.TimeOutError:
                pass
        if v in self.BAD_PLATFORM:
            # Trying CLI
            try:
                v = self.cli("display version", cached=True)
            except self.CLISyntaxError:
                raise self.NotSupportedError()
        if "NetEngine" in v or "MultiserviceEngine" in v:
            # Use specified regex for this platform
            match_re_list.insert(0, self.rx_ver_snmp4_ne_me)
        rx = self.find_re(match_re_list, v)
        match = rx.search(v)
        platform = match.group("platform")
        # Convert NetEngine to NE
        if platform.lower().startswith("netengine"):
            n, p = platform.split(" ", 1)
            platform = "NE%s" % p.strip().upper()
        elif platform.lower().startswith("multiserviceengine"):
            n, p = platform.split(" ", 1)
            platform = "ME%s" % p.strip().upper()
        # Found in AR1220 and AR1220E
        elif platform.startswith("Huawei "):
            n, p = platform.split(" ", 1)
            platform = p.strip()
        r = {
            "vendor": "Huawei",
            "platform": platform,
            "version": match.group("version")
        }
        if "image" in match.groupdict():
            image = match.group("image")
            r["attributes"] = {"image": image}
        return r
