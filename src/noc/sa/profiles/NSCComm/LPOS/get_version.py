# ----------------------------------------------------------------------
# NSCComm.LPOS.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "NSCComm.LPOS.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^System ID\s+: (?P<platform>\S+)\s*\n"
        r"^Hardware version\s+: (?P<hardware>.+)\s*\n"
        r"^Software version\s+: LP ARM OS (?P<version>.+) \(.+\n"
        r"^Firmware version\s+: (?P<fw_version>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_snmp(self, **kwargs):
        version = self.snmp.get("1.3.6.1.4.1.42926.2.3.1.2.0")
        version = " ".join(version.split()[1:3])
        hw_version = self.snmp.get("1.3.6.1.4.1.42926.2.3.1.1.0")
        return {
            "vendor": "NSCComm",
            "platform": "Sprinter TX",
            "version": version,
            "attributes": {"HW version": hw_version},
        }

    def execute_cli(self):
        try:
            v = self.cli("stats", cached=True)
        except self.CLISyntaxError:
            raise NotImplementedError
        match = self.rx_ver.search(v)
        return {
            "vendor": "NSCComm",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {"HW version": match.group("hardware")},
        }
