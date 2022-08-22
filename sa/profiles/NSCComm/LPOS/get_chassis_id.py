# ---------------------------------------------------------------------
# NSCComm.LPOS.get_chassis_id
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
    name = "NSCComm.LPOS.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^Physical Address\s+: (?P<mac>\S+)", re.MULTILINE)

    SNMP_GET_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress", 1]]}

    def execute_cli(self, **kwargs):
        if self.is_sprinter:
            raise NotImplementedError
        v = self.cli("stats", cached=True)
        match = self.rx_mac.search(v)
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
