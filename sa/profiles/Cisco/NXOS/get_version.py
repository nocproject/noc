# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Cisco.NXOS.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(
        r"^Cisco Nexus Operating System \(NX-OS\) Software.+?"
        r"Software.+?(?:system|NXOS):\s+version\s+"
        r"(?P<version>\S+).+?Hardware\s+cisco\s+\S+\s+(?P<platform>\S+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\",\s+DESCR: \"(?P<descr>[^\"]+)\"\s*\n"
        r"PID:\s+(?P<pid>\S*)\s*,\s+VID:\s+(?P<vid>\S*)\s*,\s+SN: (?P<serial>\S+)",
        re.MULTILINE,
    )
    rx_snmp_ver = re.compile(r"^Cisco NX-OS\(tm\) .*?Version (?P<version>[^,]+),", re.IGNORECASE)
    rx_snmp_platform = re.compile(r"^Nexus\s+(?P<platform>\S+).+Chassis$", re.IGNORECASE)
    rx_snmp_platform1 = re.compile(r"^(?P<platform>N\dK-C\d\d\d\d\S+)$")

    def execute(self):
        r = {"vendor": "Cisco", "version": "Unsupported", "platform": "Unsupported"}
        if self.has_snmp():
            try:
                v = self.snmp.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
                match = self.rx_snmp_ver.search(v)
                r["version"] = match.group("version")
                # Get platform via ENTITY-MIB
                # ENTITY-MIB::entPhysicalName
                for oid, v in self.snmp.getnext("1.3.6.1.2.1.47.1.1.1.1.7"):
                    match = self.rx_snmp_platform.match(v)
                    if match:
                        r["platform"] = match.group("platform")
                        break
                    match = self.rx_snmp_platform1.match(v)
                    if match:
                        r["platform"] = match.group("platform")
                        break
                return r
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show version | no-more")
        match = self.rx_ver.search(v)
        if match:
            r["version"] = match.group("version")
        # Use first chassis PID from inventory for platform
        v = self.cli("show inventory chassis | no-more")
        for match in self.rx_item.finditer(v):
            r["platform"] = match.group("pid")
            break
        return r
