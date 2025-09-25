# ---------------------------------------------------------------------
# Supertel.K2X.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "Supertel.K2X.get_chassis_id"
    interface = IGetChassisID
    cache = True

    SNMP_GETNEXT_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress"]]}

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute_cli(self, **kwargs):
        # Fallback to CLI
        match = self.rx_mac.search(self.cli("show system", cached=True))
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
