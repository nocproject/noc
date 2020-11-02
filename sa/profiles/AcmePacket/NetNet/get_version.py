# ---------------------------------------------------------------------
# AcmePacket.NetNet.get_version
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
    name = "AcmePacket.NetNet.get_version"
    interface = IGetVersion
    cache = True

    rx_snmp_version = re.compile(r"Acme Packet\s+(?P<platform>\S+\s\d+)\s(?P<version>.+)")

    def execute_snmp(self, **kwargs):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0])
        match = self.rx_snmp_version.search(v)
        if match:
            serial = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 1])
            return {
                "vendor": "AcmePacket",
                "platform": match.group("platform"),
                "version": match.group("version"),
                "attributes": {"Serial Number": serial},
            }
        raise NotImplementedError
