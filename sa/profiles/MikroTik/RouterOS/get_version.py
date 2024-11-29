# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_version"
    cache = True
    interface = IGetVersion

    # Some versions of Mikrotik return parameter values in quotes
    rx_ver = re.compile(r"^\s+version: (?P<q>\"?)(?P<version>.*)(?P=q)\s*\n", re.MULTILINE)
    rx_arch = re.compile(r"^\s+architecture-name: (?P<q>\"?)(?P<arch>.*)(?P=q)\s*\n", re.MULTILINE)
    rx_platform = re.compile(r"^\s+board-name: (?P<q>\"?)(?P<platform>.*)(?P=q)\s*\n", re.MULTILINE)
    rx_serial = re.compile(
        r"^\s+serial-number: (?P<q>\"?)(?P<serial>\S+?)(?P=q)\s*\n", re.MULTILINE
    )
    rx_boot = re.compile(r"^\s+current-firmware: (?P<q>\"?)(?P<boot>\S+?)(?P=q)\s*\n", re.MULTILINE)
    rx_platform_snmp = re.compile(r"RouterOS\s+(?P<platform>.*)")

    def execute_cli(self):
        v = self.cli("/system resource print")
        version = self.rx_ver.search(v).group("version")
        if " " in version:
            version = version.split(" ", 1)[0]
        platform = self.rx_platform.search(v).group("platform")
        match = self.rx_arch.search(v)
        if match:
            arch = match.group("arch")
            # platform = "%s (%s)" % (platform, arch)
        else:
            arch = None
        r = {"vendor": "MikroTik", "platform": platform, "version": version, "attributes": {}}
        if "x86" not in platform and "CHR" not in platform:
            v = self.cli("/system routerboard print")
            match = self.rx_serial.search(v)
            if match:
                r["attributes"]["Serial Number"] = match.group("serial")
            match = self.rx_boot.search(v)
            if match:
                r["attributes"]["Boot PROM"] = match.group("boot")
            if arch:
                r["attributes"]["Arch"] = arch
        return r

    def execute_snmp(self):
        try:
            p = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0])
        except (self.snmp.TimeOutError, self.snmp.SNMPError):
            raise NotImplementedError()

        match = self.rx_platform_snmp.search(p)

        version = self.snmp.get(mib["1.3.6.1.4.1.14988.1.1.4.4.0"])
        if not version:
            version = self.snmp.get(mib["1.3.6.1.4.1.14988.1.1.7.4.0"])

        r = {
            "vendor": "MikroTik",
            "platform": match.group("platform") if match else "",
            "version": version,
            "attributes": {},
        }

        serial = self.snmp.get(mib["1.3.6.1.4.1.14988.1.1.7.3.0"])
        if serial:
            r["attributes"]["Serial Number"] = serial

        return r
