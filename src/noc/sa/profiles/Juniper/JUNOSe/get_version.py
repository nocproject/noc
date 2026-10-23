# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_version
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
    name = "Juniper.JUNOSe.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Juniper\s+(Edge Routing Switch )?(?P<platform>.+?)$.+"
        r"Version\s+(?P<version>.+?)\s*\[BuildId (?P<build>\d+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_snmp_ver = re.compile(
        r"Juniper Networks, Inc.\s+(?P<platform>\S+).+?SW Version\s:"
        r"\s\((?P<version>[A-Za-z0-9\- \.\[\]]+)\)"
    )

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
        match = self.rx_snmp_ver.search(v)
        if match is None:
            raise self.snmp.TimeOutError()
        return {
            "vendor": "Juniper",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }

    def execute_cli(self):
        v = self.cli("show version")
        match = self.re_search(self.rx_ver, v.replace(":", ""))
        return {
            "vendor": "Juniper",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {"Build": match.group("build")},
        }
