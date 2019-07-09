# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vector.Lambda.get_version
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
    name = "Vector.Lambda.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^Device: (?P<platform>.+)\n" r"FW ver: (?P<version>\S+)\n" r"SN: (?P<serial>\d+)$",
        re.MULTILINE,
    )

    def execute_snmp(self, **kwargs):
        try:
            platform = self.snmp.get("1.3.6.1.2.1.1.1.0")  # SNMPv2-MIB::sysDescr
            version = self.snmp.get(
                "1.3.6.1.4.1.11195.1.5.2.0"
            )  # VECTOR-HFC-NODE-MIB::fnFirmwareVersion
            serial = self.snmp.get(
                "1.3.6.1.4.1.11195.1.5.1.0"
            )  # VECTOR-HFC-NODE-MIB::fnSerialNumber

            return {
                "vendor": "Vector",
                "platform": platform,
                "version": version,
                "attributes": {"Serial Number": serial},
            }
        except self.snmp.TimeOutError:
            raise self.NotSupportedError

    def execute_cli(self, **kwargs):
        cmd = self.cli("sys", cached=True)
        match = self.rx_ver.search(cmd)
        if not match:
            raise self.NotSupportedError

        return {
            "vendor": "Vector",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {"Serial Number": match.group("serial")},
        }
