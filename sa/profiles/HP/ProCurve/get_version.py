# ---------------------------------------------------------------------
# HP.ProCurve.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "HP.ProCurve.get_version"
    cache = True
    interface = IGetVersion
    always_prefer = "S"

    rx_ver = re.compile(
        r"^(?:HP|ProCurve)\s+(?:\w+)\s+(?:ProCurve\s+)?Switch\s+(?P<platform>\S+),"
        r"\s+revision\s+(?P<version>\S+),\s+ROM\s+(?P<bootprom>\S+)",
        re.MULTILINE,
    )
    rx_ver_new = re.compile(
        r"^HP\s+(?:\S+\s+)?(?P<platform>\S+)\s+Switch(?: Stack)?,"
        r"\s+revision\s+(?P<version>\S+),\s+ROM\s+(?P<bootprom>\S+)",
        re.MULTILINE,
    )

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver_new.search(v)
        return {
            "vendor": "HP",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {"Boot PROM": match.group("bootprom")},
        }

    def execute_cli(self):
        try:
            v = self.cli("walkMIB sysDescr", cached=True).replace("sysDescr.0 = ", "")
        except self.CLISyntaxError:
            raise NotImplementedError
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver_new.search(v)
        return {
            "vendor": "HP",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {"Boot PROM": match.group("bootprom")},
        }
