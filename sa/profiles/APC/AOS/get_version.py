# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# APC.AOS.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.lib.text import parse_kv
from noc.core.mib import mib


class Script(BaseScript):
    name = "APC.AOS.get_version"
    cache = True
    interface = IGetVersion

    rx_fwver = re.compile(r"Network Management Card AOS\s+v(?P<version>\S+)$",
                          re.MULTILINE)
    rx_platform = re.compile(r"^(?P<platform>.+?)\s+named\s+", re.MULTILINE)

    rx_platform1 = re.compile(r"^Name\s+: (?P<platform>.+?)\s+Date",
                              re.MULTILINE)

    def execute_snmp(self, **kwargs):
        platform = self.snmp.get("1.3.6.1.2.1.33.1.1.2.0")
        firmware = self.snmp.get("1.3.6.1.2.1.33.1.1.3.0")
        if not platform:
            # Use SysName for old version
            platform = self.snmp.get(mib["SNMPv2-MIB::sysName", 0])
        if not platform:
            raise self.NotSupportedError
        return {
            "vendor": "APC",
            "platform": platform,
            "version": firmware
        }

    def execute_cli(self):
        # Not worked for Menu CLI
        m = self.motd
        if m:
            match = self.rx_platform.search(m)
            if not match:
                match = self.rx_platform1.search(m)
            platform = match.group("platform").strip()
            version = self.re_search(self.rx_fwver, m).group("version")
        else:
            v = self.cli("upsabout")
            d = parse_kv({"model": "platform",
                          "firmware revision": "version"}, v)
            platform = d["platform"]
            version = d["version"]

        return {
            "vendor": "APC",
            "platform": platform,
            "version": version
        }
