# ---------------------------------------------------------------------
# HP.Comware.get_version
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
    name = "HP.Comware.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile(
        r"^(?P<vendor>HP|HPE|)\s*(?P<ver>\S+) Software, Version (?P<version>.+)$", re.MULTILINE
    )
    rx_devinfo_HP = re.compile(
        r"^Slot 1:\nDEVICE_NAME\s+:\s+(?P<platform>[A-Z,0-9a-z\- ]+)(\s+.+?\n|)\n"
        r"DEVICE_SERIAL_NUMBER\s+:\s+(?P<serial>\S+)\n",
        re.MULTILINE,
    )
    rx_devinfo_HPE = re.compile(
        r"\s+Slot \d+(\s+\S+\s+\d+|):\n"
        r"DEVICE_NAME\s+:\s+(?P<platform>[A-Z0-9a-z \-+]+)\n"
        r"DEVICE_SERIAL_NUMBER\s+:\s+(?P<serial>\S+)\n",
        re.MULTILINE,
    )

    rx_snmp_sw_version = re.compile(r"Software Version (?P<version>(?:\d+.?)+),?")
    rx_snmp_platform = re.compile(r"(?:HPE\s+)?(?P<platform>.+Switch)")

    def execute_cli(self, **kwargs):
        platform = "Comware"
        version = "Unknown"
        s = ""

        v = self.cli("display version")
        match = self.rx_version.search(v)
        if match:
            version = match.group("version")
            ver = match.group("ver")
            vendor = match.group("vendor") or "HP"
        if ver == "Comware":
            try:
                v = self.cli("display device manuinfo", cached=True)
                if vendor == "HP":
                    match = self.rx_devinfo_HP.search(v)
                    if match:
                        platform = match.group("platform")
                        s = match.group("serial")
                if vendor == "HPE":
                    match = self.rx_devinfo_HPE.search(v)
                    if match:
                        platform = match.group("platform")
                        s = match.group("serial")
            except self.CLISyntaxError:
                pass
        r = {"vendor": vendor, "platform": platform.strip(), "version": version, "attributes": {}}
        if not s and self.has_snmp():
            try:
                for oid, s in self.snmp.getnext(mib["ENTITY-MIB::entPhysicalSerialNum"]):
                    if s:
                        break
            except (self.snmp.TimeOutError, self.snmp.SNMPError):
                pass
        if s:
            r["attributes"]["Serial Number"] = s
        return r

    def execute_snmp(self, **kwargs):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        # v, _ = v.splitlines()
        match = self.rx_snmp_sw_version.search(v)
        if match:
            version = match.group("version")
        match = self.rx_snmp_platform.search(v)
        if match:
            platform = match.group("platform")
        return {
            "vendor": "HP",
            "platform": platform.strip(),
            "version": version.strip(", "),
            "attributes": {},
        }
