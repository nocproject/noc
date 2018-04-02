# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IBM.NOS.get_version
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
    name = "IBM.NOS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Software Version\s+(?P<version>\S+)\s\(\w+\s(?P<image>\S+)\)", re.MULTILINE
    )

    rx_ser = re.compile(
        r"Serial Number\s+\:\s+(?P<serial>\S+)", re.MULTILINE
    )

    rx_pla = re.compile(
        r"^IBM\s.*(?P<platform>(EN|CN|SI|G)\d{4}\w?)\s+", re.MULTILINE
    )

    def execute_snmp(self):
        try:
            p = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)  # sysDescr.0
            match = self.rx_pla.search(p)
            platform = match.group("platform")
            version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.1", cached=True)  # entPhysicalSoftwareRev.1
            image = self.snmp.get("1.3.6.1.2.1.25.4.2.1.2.1", cached=True)  # hrSWRunName.1
            serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1", cached=True)  # entPhysicalSerialNum.1
            return {
                "vendor": "IBM",
                "platform": platform,
                "version": version,
                "image": image,
                "attributes": {"Serial Number": serial}
            }
        except self.snmp.TimeOutError:
            pass

    def execute_cli(self):

        v = self.cli("show version | exclude Temp", cached=True)
        match1 = self.rx_pla.search(v)
        match2 = self.rx_ver.search(v)
        match3 = self.rx_ser.search(v)

        platform = match1.group("platform")
        version = match2.group("version")
        image = match2.group("image")
        serial = match3.group("serial")

        return {
            "vendor": "IBM",
            "platform": platform,
            "version": version,
            "image": image,
            "attributes": {"Serial Number": serial}
        }
