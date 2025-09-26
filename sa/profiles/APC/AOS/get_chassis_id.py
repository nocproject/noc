# ---------------------------------------------------------------------
# APC.AOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC
from noc.core.mib import mib
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "APC.AOS.get_chassis_id"
    interface = IGetChassisID

    SNMP_GET_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress", 2]]}

    def execute_cli(self):
        v = self.cli("about", cached=True)

        s = parse_kv({"mac address": "mac"}, v)
        if s:
            s = s["mac"].replace(" ", ":")
            return [{"first_chassis_mac": MAC(s), "last_chassis_mac": MAC(s)}]
        raise self.NotSupportedError
