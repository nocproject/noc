# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"system hardware version\s+:\s*(?P<hardware>\S+).+"
        r"system firmware version\s+:\s*(?P<version>\S+).+"
        r"system boot( prom)? version\s+:\s*(?P<bootprom>\S+).+"
        r"(system protocol version\s+:\s+(?P<protover>\S+).+)?"
        r"system serial number\s+:\s*(?P<serial>\S+)",
        re.MULTILINE | re.DOTALL | re.I,
    )
    rx_snmp_ver = re.compile(r"^(?:WS6-)?(?P<platform>\S+)\s*")

    def execute(self):
        r = {"vendor": "DLink"}
        try:
            v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
            match = self.rx_snmp_ver.search(v)
            r["platform"] = match.group("platform")
        except self.snmp.TimeOutError:
            raise self.NotSupportedError()
        try:
            s = self.cli("show switch", cached=True)
            match = self.rx_ver.search(s)
            r.update(
                {
                    "version": match.group("version"),
                    "attributes": {
                        "Boot PROM": match.group("bootprom"),
                        "HW version": match.group("hardware"),
                        "Serial Number": match.group("serial"),
                    },
                }
            )
            return r
        except Exception:
            raise self.NotSupportedError()
