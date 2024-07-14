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
    name = "Juniper.JUNOS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^Model:\s+(?P<platform>\S+)\s*\n" r"^Junos: (?P<version>\S+[0-9])", re.MULTILINE
    )
    rx_ver2 = re.compile(
        r"^Model:\s+(?P<platform>\S+)\s*\n" r"^JUNOS .*? \[(?P<version>\S+)\]", re.MULTILINE
    )
    # JUNOS .*? \[(?P<version>[^\]]+)\]",
    rx_snmp_ver = re.compile(
        r"Juniper Networks, Inc.\s+(?P<platform>\S+).+?JUNOS\s+" r"(?P<version>\S+[0-9])"
    )
    rx_serial = re.compile(r"Chassis\s+(?P<serial>\w+)\s", re.MULTILINE)

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
        match = self.rx_snmp_ver.search(v)
        if match:
            version = match.group("version")
            platform = match.group("platform")
        else:
            version = self.snmp.get(
                mib["JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberSWVersion", 0]
            )
            platform = self.snmp.get(
                mib["JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberModel", 0]
            )
        return {
            "vendor": "Juniper",
            "platform": platform,
            "version": version,
        }

    def execute_cli(self):
        v = self.cli("show version")
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver2.search(v)
        r = {
            "vendor": "Juniper",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
        try:
            s = self.cli("show chassis hardware", cached=True)
            match_ser = self.rx_serial.search(s)
            if match_ser:
                r["attributes"] = {}
                r["attributes"]["Serial Number"] = match_ser.group("serial")
        except self.CLISyntaxError:
            pass
        return r
