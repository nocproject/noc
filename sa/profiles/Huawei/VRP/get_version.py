# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
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
        r"(?P<platform>(?:\S+\s+)?S\d+(?:[A-Z]+-[A-Z]+)?(?:\d+\S+)?)"
        r"\s+Huawei\sVersatile\sRouting\sPlatform"
        r"\sSoftware.*Version\s(?P<version>\d+\.\d+)\s"
        r"\(S\d+\s(?P<image>\S+)+\).*",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    rx_ver_snmp3 = re.compile(
        r"^\s*VRP.+Software, Version (?P<version>\S+)\s+"
        r"\((?P<platform>S\S+|CX\d+) (?P<image>[^)]+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    rx_ver_snmp4 = re.compile(
        r"Huawei Versatile Routing Platform Software.*?"
        r"Version (?P<version>\S+) .*?"
        r"\s*(?:Quidway|Huawei) (?P<platform>(?:NetEngine\s+|MultiserviceEngine\s+)?\S+)[^\n]\d",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    rx_ver_snmp5 = re.compile(
        r"Huawei Versatile Routing Platform.*?"
        r"Version (?P<version>\S+) .*?"
        r"\s*(?:Quidway|Huawei) (?P<platform>[A-Z0-9]+)\s",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    def execute(self):
        v = ""
        if self.has_snmp():
            # Trying SNMP
            try:
                # SNMPv2-MIB::sysDescr.0
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
            except self.snmp.TimeOutError:
                pass
        if v == "":
            # Trying CLI
            try:
                v = self.cli("display version", cached=True)
            except self.CLISyntaxError:
                raise self.NotSupportedError()
        rx = self.find_re([
            self.rx_ver,
            self.rx_ver_snmp,
            self.rx_ver_snmp2,
            self.rx_ver_snmp3,
            self.rx_ver_snmp4,
            self.rx_ver_snmp5
        ], v)
        match = rx.search(v)
        platform = match.group("platform")
        # Convert NetEngine to NE
        if platform.lower().startswith("netengine"):
            n, p = platform.split(" ", 1)
            platform = "NE%s" % p.strip().upper()
        elif platform.lower().startswith("multiserviceengine"):
            n, p = platform.split(" ", 1)
            platform = "ME%s" % p.strip().upper()
        r = {
            "vendor": "Huawei",
            "platform": platform,
            "version": match.group("version")
        }
        if "image" in match.groupdict():
            image = match.group("image")
            r["attributes"] = {"image": image}
        return r
