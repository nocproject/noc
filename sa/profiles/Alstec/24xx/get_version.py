# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alstec.24xx.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^System Description(\s+|\.+)\s*(:|)\s*(?P<platform>\S+).+?"
        r"^Bootloader\sVersion\s+:\s+(CFE |U-Boot )?(?P<bootprom>\S+)(\s\(.+\)|)\s*\n"
        r"^OS Version.+\n"
        r"^Software version\s+:\s+(?P<version>\S+)\s*\n"
        r"Software type\s+:\s+(?P<fwt>\S+)\s*\n",
        re.MULTILINE)
    rx_serial = re.compile("Serial Number\.+ (?P<serial>\S+)")
    rx_platform = re.compile("Machine Model\.+ (?P<platform>\S+)")
    rx_version = re.compile("Software Version\.+ (?P<version>\S+)")
    rx_ver2 = re.compile(
        r"^Machine Model\.+\s*(?P<platform>\S+)"
        r"^Serial Number\.+\s*(?P<serial>\S+).*"
        r"^Software Version\.+\s*(?P<version>\S+)"
        r"^Operating System\.+\s*(?P<os_version>.+)"
        r"^Network", re.MULTILINE | re.DOTALL
    )

    def execute(self):

        v = self.cli("show sysinfo", cached=True)
        match = self.rx_ver.search(v)
        if match:
            v = self.cli("show hardware", cached=True)
            match1 = self.rx_serial.search(v)
            s = {"Boot PROM": match.group("bootprom"),
                 "Firmware Type": match.group("fwt"),
                 "Serial Number": match1.group("serial")}
        else:
            v = self.cli("show hardware", cached=True)
            # match = self.rx_ver2.search(v)
            s = {"Serial Number": self.rx_serial.search(v).group("serial")}
            return {
                "vendor": "Alstec",
                "platform": self.rx_platform.search(v).group("platform"),
                "version": self.rx_version.search(v).group("version"),
                "attributes": s

            }

        return {
            "vendor": "Alstec",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": s
        }
