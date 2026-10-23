# ---------------------------------------------------------------------
# Cambium.ePMP.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cambium.ePMP.get_chassis_id"
    cache = True
    interface = IGetChassisID

    SNMP_GET_OIDS = {
        "SNMP": [
            mib["CAMBIUM-PMP80211-MIB::cambiumLANMACAddress", 0],
            mib["CAMBIUM-PMP80211-MIB::cambiumWirelessMACAddress", 0],
        ]
    }

    def execute_cli(self, **kwargs):
        # Replace # with @ to prevent prompt matching
        r = {}
        v = self.cli("show dashboard", cached=True).strip()
        for e in v.splitlines():
            e = e.strip().split(" ", 1)
            if len(e) == 2:
                r[e[0]] = e[1].strip()
            else:
                r[e[0]] = None
        if r["cambiumConnectedAPMACAddress"]:
            return {
                "first_chassis_mac": r["cambiumConnectedAPMACAddress"],
                "last_chassis_mac": r["cambiumConnectedAPMACAddress"],
            }
