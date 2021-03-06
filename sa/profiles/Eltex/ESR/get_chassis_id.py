# ---------------------------------------------------------------------
# Eltex.ESR.get_chassis_id
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
    name = "Eltex.ESR.get_chassis_id"
    interface = IGetChassisID
    cache = True

    SNMP_GETNEXT_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress"]]}

    rx_mac = re.compile(r"^\s*System MAC address:\s+(?P<mac>\S+)", re.MULTILINE)

    def execute_cli(self):
        c = self.scripts.get_system()
        match = self.rx_mac.search(c)
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
