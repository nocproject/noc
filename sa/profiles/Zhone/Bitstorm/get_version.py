# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.Bitstorm.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.lib.text import parse_table
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Zhone.Bitstorm.get_version"
    cache = True
    interface = IGetVersion

    # 1.3.6.1.4.1.1795.1.14.9.14.5.3
    """
    System Name              d01.cn.kms
    System Location
    System Contact
    System Description       Paradyne DSLAM; Model: 8820-A2-xxx
    """
    # rx_ver = re.compile(r"software version MXK (?P<version>\S+)")
    rx_platform = re.compile(r"^(?P<platform>MXK \d+)\s*\n", re.MULTILINE)
    rx_ver = re.compile(r"^FW Rev\s*(?P<version>\S+)\n"
                        r"^Model\s*(?P<platform>\S+)\n"
                        r"^Serial Number\s*(?P<serial>\S+)\n"
                        r"^MAC Address Eth1\s*(?P<mac1>\S+)\n"
                        r"^MAC Address Eth2\s*(?P<mac2>\S+)\n", re.MULTILINE | re.IGNORECASE)

    rx_ver2 = re.compile(r"\s*System Name\s*(?P<hostname>\S*)(\s*\n)"
                         r"\s*System Location\s*(?P<location>\S*)(\s*\n)"
                         r"\s*System Contact\s*(?P<contact>\S*)(\s*\n)"
                         r"\s*System Description\s*(?P<description>.*)", re.MULTILINE | re.IGNORECASE)

    def execute(self):
        v = self.cli("show system information", cached=True)
        platform = "Unknown"
        version = ""
        if "Paradyne DSLAM" in v or "Zhone DSLAM" in v:
            match = self.rx_ver2.match(v)
            if match:
                platform = match.group("description")
                platform = platform.split(";")[1].split(":")[1].strip()
            v = self.cli("show system status", cached=True)
            v = parse_table(v)
            for l in v:
                # if "Slot A (SCP)" in l[0]:
                if "SCP" in l[0] or "MCP" in l[0]:
                    version = l[1]
        else:
            match = self.re_search(self.rx_ver, v)
            version = match.group("version")
            # v = self.cli("slots", cached=True)
            # match = self.re_search(self.rx_platform, v)
            platform = match.group("platform")
        return {
            "vendor": "Zhone",
            "version": version,
            "platform": platform
        }
