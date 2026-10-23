# ---------------------------------------------------------------------
# Mellanox.Cumulus.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.text import parse_table
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Mellanox.Cumulus.get_chassis_id"
    interface = IGetChassisID
    cache = True

    def execute_cli(self):
        v = self.cli("decode-syseeprom", cached=True)
        for i in parse_table(v, max_width=250):
            if i[0] == "Base MAC Address":
                base = i[3]
            elif i[0] == "MAC Addresses":
                count = int(i[3])
        return [{"first_chassis_mac": base, "last_chassis_mac": MAC(base).shift(count - 1)}]
