# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ericsson.SEOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Ericsson.SEOS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^Active SBL\s+:\s+CXP:\s+(?P<version>\S+.*)\s+"
        r"^Passive (?:NPU|SBL)\s+:\s+CXP:\s+[\S\s]+"
        r"^Active BNS\s+:\s+CXCR:\s+(?P<sw_backup>\S+.*)\s+"
        r"^Subrack\s+:\s+(?P<platform>\S+.*)\s+\-",
        re.MULTILINE,
    )

    def execute_snmp(self):
        platform = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
        active_rev = self.snmp.get("1.3.6.1.4.1.193.81.2.7.1.3.0", cached=True)
        version = self.snmp.get("1.3.6.1.4.1.193.81.2.7.1.2.1.3.%s" % active_rev, cached=True)
        serial = self.snmp.get("1.3.6.1.4.1.193.81.2.7.1.2.1.2.%s" % active_rev, cached=True)
        return {
            "vendor": "Ericsson",
            "platform": platform.replace("Traffic Node", "TN").replace("Compact Node", "CN"),
            "version": version,
            "attributes": {"Serial Number": serial},
        }

    def execute_cli(self):
        ver = self.cli("show version", cached=True)
        for match in self.rx_ver.finditer(ver):
            version = match.group("version")
            sw_backup = match.group("sw_backup")
            platform = match.group("platform")
            return {
                "vendor": "Ericsson",
                "platform": platform.replace("Traffic Node", "TN").replace("Compact Node", "CN"),
                "version": version.strip(),
                "attributes": {"sw_backup": sw_backup},
            }
