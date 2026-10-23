# ---------------------------------------------------------------------
# Enterasys.EOS.get_version
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
    name = "Enterasys.EOS.get_version"
    interface = IGetVersion
    cache = True

    rx_platform = re.compile(r"^Enterasys Networks, Inc. (?P<platform>\S+) Rev (?P<version>\S+)$")

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        match = self.rx_platform.search(v)
        r = {
            "vendor": "Enterasys",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {},
        }
        for oid, name in self.snmp.getnext(mib["ENTITY-MIB::entPhysicalSerialNum"]):
            if name:
                r["attributes"]["Serial Number"] = name
                break
        for oid, name in self.snmp.getnext(mib["ENTITY-MIB::entPhysicalHardwareRev"]):
            if name:
                r["attributes"]["HW version"] = name
                break
        for oid, name in self.snmp.getnext(mib["ENTITY-MIB::entPhysicalFirmwareRev"]):
            if name:
                r["attributes"]["Boot PROM"] = name
                break
        return r
