# ---------------------------------------------------------------------
# HP.OfficeConnect.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "HP.OfficeConnect.get_version"
    interface = IGetVersion
    cache = True

    rx_platform = re.compile(r"HPE OfficeConnect Switch\s+(?P<platform>.+)")

    def execute_snmp(self):
        # HPE OfficeConnect Switch 1920S 24G 2SFP JL381A, PD.01.07, Linux 3.6.5-ac96795c, U-Boot 2012.10-00118-g3773021 (Oct 11 2016 - 15:39:54)
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        platform, version, _, hw, *_ = v.split(",")
        match = self.rx_platform.match(platform)
        if not match:
            raise self.NotSupportedError("Not supported platform: %s" % platform)
        bootprom = hw.split()[1].strip()
        return {
            "vendor": "HP",
            "platform": match.group("platform").strip(),
            "version": version.strip(),
            "attributes": {"Boot PROM": bootprom},  # , "Serial Number": serial},
        }
