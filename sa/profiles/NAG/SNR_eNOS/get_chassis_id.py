# ---------------------------------------------------------------------
# NAG.SNR_eNOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "NAG.SNR_eNOS.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^\S+\s+mac\s+(\S+)\s*\n", re.MULTILINE | re.IGNORECASE)
    #rx_mac2 = re.compile(r"^MAC address\s+: (?P<mac>\S+)", re.MULTILINE)

    SNMP_GET_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress", 1]]}

    def execute_cli(self):
        #if self.is_foxgate_cli:
        #    macs = sorted(self.rx_mac2.findall(self.cli("show ip", cached=True)))
        #else:
        macs = sorted(self.rx_mac.findall(self.cli("show version", cached=True)))
        return [
            {"first_chassis_mac": f, "last_chassis_mac": t} for f, t in self.macs_to_ranges(macs)
        ]
