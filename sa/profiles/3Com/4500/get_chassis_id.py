# ---------------------------------------------------------------------
# 3Com.4500.get_chassis_id
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
    name = "3Com.4500.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^\s+First mac address\s+:\s+(?P<mac>\S+)$", re.MULTILINE)

    SNMP_GETNEXT_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress"]]}

    def execute_cli(self):
        v = self.cli("display device manuinfo", cached=True)
        match = self.rx_mac.search(v)
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
