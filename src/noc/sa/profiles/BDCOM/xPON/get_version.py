# ---------------------------------------------------------------------
# BDCOM.xPON.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "BDCOM.xPON.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"BDCOM\S+\s+(?P<platform>\S+)\s+\S+\s+Version\s+(?P<version>\S+)\s"
        r"Build\s(?P<build>\d+).+System Bootstrap,\s*Version\s(?P<boot>\S+),"
        r"\s*Serial num:(?P<serial>\d+)",
        re.MULTILINE | re.DOTALL,
    )

    # todo: add hardware ver for P3310C, P3608 (snmp output need)
    # rx_hver = re.compile(r"^hardware version:(?:V|)(?P<hversion>\S+)", re.MULTILINE)

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
        match = self.rx_ver.search(v)
        return {
            "vendor": "BDCOM",
            "platform": match.group("platform"),
            "version": f"{match.group('version')}, {match.group('build')}",
            "attributes": {
                "Build": match.group("build"),
                "Boot PROM": match.group("boot"),
                "Serial Number": match.group("serial"),
            },
        }

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        if match:
            return {
                "vendor": "BDCOM",
                "platform": match.group("platform"),
                "version": f"{match.group('version')}, {match.group('build')}",
                "attributes": {
                    "Build": match.group("build"),
                    "Boot PROM": match.group("boot"),
                    "Serial Number": match.group("serial"),
                },
            }
        raise self.NotSupportedError()
