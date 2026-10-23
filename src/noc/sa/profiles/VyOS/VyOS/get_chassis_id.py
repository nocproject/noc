# ---------------------------------------------------------------------
# VyOS.VyOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "VyOS.VyOS.get_chassis_id"
    interface = IGetChassisID
    always_prefer = "S"

    rx_mac = re.compile(r"^\s+link/ether (\S+)\s+brd", re.MULTILINE)

    SNMP_GET_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress", 1]]}

    def execute_cli(self):
        c = self.cli("show interfaces detail", cached=True)
        macs = sorted(self.rx_mac.findall(c))
        return [
            {"first_chassis_mac": f, "last_chassis_mac": t} for f, t in self.macs_to_ranges(macs)
        ]
