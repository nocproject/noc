# ---------------------------------------------------------------------
# Cambium.ePMP.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cambium.ePMP.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile(r"^\S+\.v(?P<version>[^@]+)$")

    def execute_snmp(self, **kwargs):
        version = self.snmp.get(mib["CAMBIUM-PMP80211-MIB::cambiumCurrentSWInfo", 0])
        sn = self.snmp.get(mib["CAMBIUM-PMP80211-MIB::cambiumESN", 0])
        if sn == "N/A":
            sn = self.snmp.get(mib["CAMBIUM-PMP80211-MIB::cambiumEPMPMSN", 0])
        # cambiumESN
        boot_prom = self.snmp.get(mib["CAMBIUM-PMP80211-MIB::cambiumUbootVersion", 0])
        return {
            "vendor": "Cambium",
            "platform": "ePMP1000",
            "version": version,
            "attributes": {
                "Boot PROM": boot_prom,
                "Serial Number": sn,
            },
        }

    def execute_cli(self):
        # Replace # with @ to prevent prompt matching
        r = {}
        v = self.cli("show dashboard", cached=True).strip()
        for e in v.splitlines():
            e = e.strip().split(" ", 1)
            if len(e) == 2:
                r[e[0]] = e[1].strip()
            else:
                r[e[0]] = None

        return {
            "vendor": "Cambium",
            "platform": "ePMP1000",
            "version": r["cambiumCurrentuImageVersion"],
            "attributes": {
                "Boot PROM": r["cambiumUbootVersion"],
                "Serial Number": r["cambiumEPMPMSN"],
            },
        }
