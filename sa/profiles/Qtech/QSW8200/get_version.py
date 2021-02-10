# ---------------------------------------------------------------------
# Qtech.QSW8200.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Qtech.QSW8200.get_version"
    interface = IGetVersion
    cache = True

    always_prefer = "S"

    rx_ver = re.compile(
        r"Product Name: (?P<platform>.*)\s*\n"
        r"(Product Version:.*\n)?"
        r"Hardware Version:(?P<hardware>.*)\n"
        r"Software Version: (?P<version>\S+)\(.+\)\s*\n"
        r"Q?OS Version:.*(\nREAP Version:)?.*\n"
        r"Bootrom Version:(?P<bootprom>.*)\n"
        r"\s*\n"
        r"System MAC Address:.*\n"
        r"Serial number:(?P<serial>.*)\n",
        re.MULTILINE,
    )

    def execute_snmp(self, **kwargs):
        # Try SNMP first
        sysdesr = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0])
        if "##" in sysdesr:
            # QOS_5.2.1 (Compiled Mar 29 2019,14:37:05)
            r = {
                ll.split(":")[0].strip().lower(): ll.split(":")[1].strip()
                for ll in sysdesr.split("##")
                if ":" in ll
            }
            platform = r["product name"]
            version = r["qos version"]
            bootprom = r["boot room version"]
            serial = r["serial number"]
        else:
            # QOS_.QSW-8200-28F.2017911.3.41.307(Compiled Sep 11 2017 18:09:48)
            platform = self.snmp.get("1.3.6.1.4.1.8886.6.1.1.1.19.0")
            version = self.snmp.get("1.3.6.1.4.1.8886.6.1.1.1.1.0")
            if not version:
                # QSW-8200-28F 3.41.307
                version = self.snmp.get("1.3.6.1.4.1.8886.6.1.1.1.16.0").split()[1]
            serial = self.snmp.get("1.3.6.1.4.1.8886.6.1.1.1.14.0")
            bootprom = self.snmp.get("1.3.6.1.4.1.8886.6.1.1.1.13.0")
            if bootprom and "/" in bootprom:
                _, bootprom = bootprom.split("/")
        return {
            "vendor": "Qtech",
            "platform": platform,
            "version": version,
            "attributes": {"Boot PROM": bootprom.strip(), "Serial Number": serial},
        }

    def execute_cli(self, **kwargs):
        ver = self.cli("show version", cached=True)
        match = self.rx_ver.search(ver)
        platform = match.group("platform")
        version = match.group("version")
        bootprom = match.group("bootprom")
        hardware = match.group("hardware")
        serial = match.group("serial")
        r = {"vendor": "Qtech", "platform": platform, "version": version, "attributes": {}}
        if serial and serial.strip():
            r["attributes"]["Serial Number"] = serial.strip()
        if bootprom and bootprom.strip():
            r["attributes"]["Boot PROM"] = bootprom.strip()
        if hardware and hardware.strip():
            r["attributes"]["HW version"] = hardware.strip()
        return r
