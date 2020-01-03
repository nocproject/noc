# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Planar.SDO3000.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "Planar.SDO3000.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"\s+Serial No\s+:\s+(?P<serial>\d+)\n"
        r"\s+H/W Version:\s+(?P<hw_ver>\S+)\n"
        r"\s+S/W Version:\s+(?P<sw_ver>\S+)\n",
        re.MULTILINE,
    )
    rx_platform = re.compile(r"\[\s+(?P<platform>[A-Z0-9]+)/")

    def execute_snmp(self, **kwargs):
        try:
            platform = self.snmp.get("1.3.6.1.2.1.1.1.0")  # SNMPv2-MIB::sysDescr
            version = self.snmp.get(
                "1.3.6.1.4.1.32108.1.7.1.3.0"
            )  # PLANAR-sdo3002-MIB::softVersion
            serial = self.snmp.get(
                "1.3.6.1.4.1.32108.1.7.1.1.0"
            )  # PLANAR-sdo3002-MIB::serialNumber
            hw_ver = self.snmp.get("1.3.6.1.4.1.32108.1.7.1.2.0")  # PLANAR-sdo3002-MIB::hardVersion

            return {
                "vendor": "Planar",
                "platform": platform.upper(),
                "version": version.strip(smart_text("\x00")),
                "attributes": {
                    "Serial Number": serial.strip(smart_text("\x00")),
                    "HW version": hw_ver.strip(smart_text("\x00")),
                },
            }
        except self.snmp.TimeOutError:
            raise self.NotSupportedError

    def execute_cli(self, **kwargs):
        cmd = self.cli("1", cached=True)
        match_p = self.rx_platform.search(cmd)
        match_v = self.rx_ver.search(cmd)
        if not (match_v and match_p):
            raise self.NotSupportedError

        return {
            "vendor": "Planar",
            "platform": match_p.group("platform"),
            "version": match_v.group("sw_ver"),
            "attributes": {
                "Serial Number": match_v.group("serial"),
                "HW version": match_v.group("hw_ver"),
            },
        }
