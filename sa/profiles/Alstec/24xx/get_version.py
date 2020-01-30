# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_version
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
    name = "Alstec.24xx.get_version"
    interface = IGetVersion
    always_prefer = "S"
    cache = True

    rx_ver = re.compile(
        r"^System Description(\s+|\.+)\s*(:|)\s*(?P<platform>\S+).+?"
        r"^Bootloader\sVersion\s+:\s+(CFE |U-Boot )?(?P<bootprom>\S+)(\s\(.+\)|)\s*\n"
        r"^OS Version.+\n"
        r"^Software version\s+:\s+(?P<version>\S+)\s*\n"
        r"Software type\s+:\s+(?P<fwt>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_serial = re.compile(r"Serial Number\.+ (?P<serial>\S+)")
    rx_platform = re.compile(r"Machine Model\.+ (?P<platform>\S+)")
    rx_version = re.compile(r"Software Version\.+ (?P<version>\S+)")
    rx_ver2 = re.compile(
        r"^Machine Model\.+\s*(?P<platform>\S+)"
        r"^Serial Number\.+\s*(?P<serial>\S+).*"
        r"^Software Version\.+\s*(?P<version>\S+)"
        r"^Operating System\.+\s*(?P<os_version>.+)"
        r"^Network",
        re.MULTILINE | re.DOTALL,
    )

    def execute_snmp(self, **kwargs):
        try:
            platform = self.snmp.get("1.3.6.1.4.1.27142.1.1.1.1.1.3.0", cached=True)
            serial = self.snmp.get("1.3.6.1.4.1.27142.1.1.1.1.1.4.0", cached=True)
            version = self.snmp.get("1.3.6.1.4.1.27142.1.1.1.1.1.13.0")
        except Exception:
            raise NotImplementedError
        if not platform:
            # if device output
            # SNMPv2-SMI::enterprises.27142.1.1.1.2.2.1.0 = "" (on device SNMPv2-SMI::enterprises.4413)
            raise NotImplementedError
        return {
            "vendor": "Alstec",
            "platform": platform,
            "version": version,
            "attributes": {"Serial Number": serial},
        }

    def execute_cli(self, **kwargs):
        v = self.cli("show sysinfo", cached=True)
        match = self.rx_ver.search(v)
        if match:
            r = {
                "vendor": "Alstec",
                "platform": match.group("platform"),
                "version": match.group("version"),
                "attributes": {
                    "Boot PROM": match.group("bootprom"),
                    "Firmware Type": match.group("fwt"),
                },
            }
            v = self.cli("show hardware", cached=True)
            match = self.rx_serial.search(v)
            if match:
                r["attributes"]["Serial Number"] = match.group("serial")
        else:
            v = self.cli("show hardware", cached=True)
            r = {
                "vendor": "Alstec",
                "platform": self.rx_platform.search(v).group("platform"),
                "version": self.rx_version.search(v).group("version"),
            }
            match = self.rx_serial.search(v)
            if match:
                r["attributes"] = {}
                r["attributes"]["Serial Number"] = match.group("serial")
        return r
