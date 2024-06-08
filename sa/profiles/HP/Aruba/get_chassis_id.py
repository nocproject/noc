# ---------------------------------------------------------------------
# HP.Aruba.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.text import parse_kv
from noc.core.mib import mib


class Script(BaseScript):
    name = "HP.Aruba.get_chassis_id"
    interface = IGetChassisID

    SNMP_GET_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress", 3718]]}
    parse_map = {
        "base mac address": "mac",
    }

    def execute_cli(self):
        v = self.cli("show system", cached=True)
        v = parse_kv(self.parse_map, v)
        return {"first_chassis_mac": v["mac"], "last_chassis_mac": v["mac"]}
