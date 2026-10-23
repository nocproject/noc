# ---------------------------------------------------------------------
# Mellanox.Onyx.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Mellanox.Onyx.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^\s+Chassis id: (\S+)\s*\n", re.MULTILINE)

    def execute_cli(self):
        c = self.cli("show lldp local", cached=True)
        mac = self.rx_mac.search(c).group(1)
        return [{"first_chassis_mac": mac, "last_chassis_mac": mac}]
