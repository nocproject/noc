# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.mib import mib
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(
        r"System description\s+:\s+(?P<platform>\S+).+System hardware version"
        r"\s+:\s+(?P<hversion>\S+?),?\s+System software version"
        r"\s+:\s+v(?P<version>\S+?),?\s+Release\(\d+\)",
        re.MULTILINE | re.DOTALL,
    )
    rx_ver1 = re.compile(
        r"^(?P<platform>D\S+)\s+System Version\s*.+?"
        r"Backplane H/W version:(?P<hversion>\S+)\s+.+?"
        r"Serial#:(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL,
    )
    rx_ver2 = re.compile(
        r"Bootloader:\s+(?P<bootprom>\S+)\s*\n\s+Runtime:\s+(?P<version>\S+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_snmp = re.compile(r"\d+", re.MULTILINE | re.DOTALL)

    def execute_cli(self):
        c = self.cli("show version", cached=True)
        match = self.rx_ver.search(c)
        if match:
            snmp_sn = (
                self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum.1"])
                if self.has_snmp()
                else None
            )
            if snmp_sn is not None:
                snmp_sn = self.rx_snmp.search(snmp_sn).group(0)
            return {
                "vendor": "DLink",
                "platform": match.group("platform"),
                "version": match.group("version"),
                "attributes": {"HW version": match.group("hversion"), "Serial Number": snmp_sn},
            }
        match = self.rx_ver1.search(c)
        if match:
            match1 = self.rx_ver2.search(c)
            return {
                "vendor": "DLink",
                "platform": match.group("platform"),
                "version": match1.group("version"),
                "attributes": {
                    "Boot PROM": match1.group("bootprom"),
                    "HW version": match.group("hversion"),
                    "Serial Number": match.group("serial"),
                },
            }
        raise self.NotSupportedError()
