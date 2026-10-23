# ---------------------------------------------------------------------
# Alentis.NetPing.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "Alentis.NetPing.get_chassis_id"
    interface = IGetChassisID
    cache = True

    always_prefer = "S"

    SNMP_GET_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress", 1]]}

    def execute_cli(self, **kwargs):
        # Fallback to HTTP
        data = self.profile.var_data(self, "/setup_get.cgi")
        mac = data["mac"]
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
