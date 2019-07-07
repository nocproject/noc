# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Eltex.MES.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.MES.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)
    rx_mac2 = re.compile(r"^OOB MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)

    SNMP_GET_OIDS = {
        "SNMP": [
            mib["BRIDGE-MIB::dot1dBaseBridgeAddress", 0],
            mib["LLDP-MIB::lldpLocChassisId", 0],
            "1.3.6.1.4.1.89.53.4.1.7.1",  # rlPhdStackMacAddr
        ]
    }
    SNMP_GETNEXT_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress"]]}

    def execute_cli(self):
        r = []
        if self.has_capability("Stack | Members"):
            for unit in self.capabilities["Stack | Member Ids"].split(" | "):
                c = self.cli("show system unit %s" % unit, cached=True)
                match = self.rx_mac.search(c)
                if not match:
                    continue
                mac_begin = match.group("mac")
                match = self.rx_mac2.search(c)
                if match:
                    mac_end = match.group("mac")
                else:
                    mac_end = mac_begin
                r += [{"first_chassis_mac": mac_begin, "last_chassis_mac": mac_end}]

        else:
            c = self.cli("show system", cached=True)
            match = self.rx_mac.search(c)
            mac_begin = match.group("mac")
            mac_end = match.group("mac")
            r = [{"first_chassis_mac": mac_begin, "last_chassis_mac": mac_end}]
        return r
