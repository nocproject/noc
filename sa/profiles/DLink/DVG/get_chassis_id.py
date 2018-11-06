# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DVG.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "DLink.DVG.get_chassis_id"
    interface = IGetChassisID
    # Always try SNMP first
    always_prefer = "S"

    rx_mac = re.compile(r"^WAN MAC \[+(?P<mac>\S+)+\]$", re.MULTILINE)
    SNMP_GET_OIDS = {
        "SNMP": mib["IF-MIB::ifPhysAddress", 2]
    }

    def execute_cli(self):
        r = self.cli("GET STATUS WAN", cached=True)
        match = self.re_search(self.rx_mac, r)
        if not match:
            raise self.NotSupportedError()
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
