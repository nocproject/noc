# ---------------------------------------------------------------------
# NAG.SNR_eNOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
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

    SNMP_GET_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress", 1]]}

    def execute_cli(self):
        macs = sorted(self.rx_mac.findall(self.cli("show version", cached=True)))
        return [
            {"first_chassis_mac": f, "last_chassis_mac": t} for f, t in self.macs_to_ranges(macs)
        ]
