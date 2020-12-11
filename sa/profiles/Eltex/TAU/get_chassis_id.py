# ---------------------------------------------------------------------
# Eltex.TAU.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Eltex.TAU.get_chassis_id"
    interface = IGetChassisID
    cache = True
    always_prefer = "S"

    SNMP_GET_OIDS = {"SNMP": ["1.3.6.1.4.1.35265.4.15.0"]}

    def execute_cli(self):
        c = self.cli("show hwaddr")
        s = c.split(":", 1)[1].strip()
        return {"first_chassis_mac": MAC(s), "last_chassis_mac": MAC(s)}
