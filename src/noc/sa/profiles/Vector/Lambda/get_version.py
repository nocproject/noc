# ----------------------------------------------------------------------
# Vector.Lambda.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Vector.Lambda.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^Device: (?P<platform>.+)\nFW ver: (?P<version>\S+)\nSN: (?P<serial>\d+)$",
        re.MULTILINE,
    )

    def execute_snmp(self, **kwargs):
        try:
            version_oid = "1.3.6.1.4.1.11195.1.5.2.0"  # VECTOR-HFC-NODE-MIB::fnFirmwareVersion
            sn_oid = "1.3.6.1.4.1.11195.1.5.1.0"  # VECTOR-HFC-NODE-MIB::fnSerialNumber
            platform = self.snmp.get(mib["SNMPv2-MIB::sysDescr"])  # SNMPv2-MIB::sysDescr
            if "VectraR2D2" in platform:
                version_oid = "1.3.6.1.4.1.30886.2.1.3.1.9.0"
                sn_oid = "1.3.6.1.4.1.17409.1.3.3.2.2.1.5.1"
            if "VS5793" in platform:
                platform = "VS5793"
            version = self.snmp.get(version_oid)
            serial = self.snmp.get(sn_oid)

            return {
                "vendor": "Vector",
                "platform": platform,
                "version": version,
                "attributes": {"Serial Number": serial},
            }
        except self.snmp.TimeOutError:
            raise NotImplementedError

    def execute_cli(self, **kwargs):
        cmd = self.cli("sys", cached=True)
        match = self.rx_ver.search(cmd)
        if not match:
            raise self.NotSupportedError

        return {
            "vendor": "Vector",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {"Serial Number": match.group("serial")},
        }
