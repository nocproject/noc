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
        if self.has_snmp():
            try:
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                match = self.re_search(self.rx_snmp_ver, v)
                r.update({"platform": match.group("platform")})
            except self.snmp.TimeOutError:
                pass
        else:
            raise self.NotSupportedError()
        if self.is_has_cli:
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
        else:
            raise self.NotSupportedError()
