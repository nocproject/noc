# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.OS62xx.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alcatel.OS62xx.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(r"^System Description:\s+(?P<platform>.+)\n", re.MULTILINE)
    rx_ser = re.compile(r"^System Serial Number:\s+(?P<serial>\S+)\n", re.MULTILINE)
    rx_ver = re.compile(r"^SW version\s+(?P<version>\S+)", re.MULTILINE)
    rx_boot = re.compile(r"^Boot version\s+(?P<boot>\S+)", re.MULTILINE)
    rx_hw = re.compile(r"^HW version\s+(?P<hw>\S+)", re.MULTILINE)

    def execute_snmp(self):
        platform = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.7.68420352",
                                 cached=True)  # Platform
        hwver = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.67108992",
                              cached=True)  # HW Version
        fwver = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.67108992",
                              cached=True)  # FW version
        bprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.67108992",
                              cached=True)  # Boot PROM
        serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.67108992",
                               cached=True)  # Serial number
        return {
            "vendor": "Alcatel",
            "platform": platform,
            "version": fwver,
            "attributes": {
                "Boot PROM": bprom,
                "HW version": hwver,
                "Serial Number": serial
            }
        }

    def execute_cli(self):
        v = self.cli("show system", cached=True)
        match_sys = self.rx_sys.search(v)
        match_ser = self.rx_ser.search(v)
        v = self.cli("show version")
        match_ver = self.rx_ver.search(v)
        r = {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version"),
            "attributes": {}
        }
        if match_ser:
            r["attributes"]["Serial Number"] = match_ser.group("serial")
        match = self.rx_boot.search(v)
        if match:
            r["attributes"]["Boot PROM"] = match.group("boot")
        match = self.rx_hw.search(v)
        if match:
            r["attributes"]["HW version"] = match.group("hw")

        return r
