# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTP.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.LTP.get_chassis_id"
    interface = IGetChassisID
    cache = True
    always_prefer = "S"

    SNMP_GET_OIDS = {
        "SNMP": [
            mib["BRIDGE-MIB::dot1dBaseBridgeAddress", 0],
            mib["LLDP-MIB::lldpLocChassisId", 0],
            "1.3.6.1.4.1.35265.1.22.1.1.9.0",
        ]
    }

    rx_mac = re.compile(r"^\s+MAC:\s+(?P<mac>\S+)\s*\n", re.MULTILINE)

    def execute_cli(self, **kwargs):
        mac = self.cli("show system environment", cached=True)
        match = self.rx_mac.search(mac)
        if not match:
            raise NotImplementedError
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
