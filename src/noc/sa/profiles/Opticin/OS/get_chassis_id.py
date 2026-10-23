# ---------------------------------------------------------------------
# Opticin.OS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID, MACAddressParameter
from noc.core.mib import mib


class Script(BaseScript):
    name = "Opticin.OS.get_chassis_id"
    cache = True
    interface = IGetChassisID
    rx_mac = re.compile(r"System MAC[^:]*?:\s*(?P<id>\S+)", re.IGNORECASE | re.MULTILINE)

    SNMP_GETNEXT_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress"]]}

    def execute_cli(self, **kwargs):
        # Fallback to CLI
        v = self.cli("show system")
        match = self.re_search(self.rx_mac, v)
        mac = MACAddressParameter().clean(match.group("id"))
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
