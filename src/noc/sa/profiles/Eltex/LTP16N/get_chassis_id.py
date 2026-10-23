# ---------------------------------------------------------------------
# Eltex.LTP16N.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Eltex.LTP16N.get_chassis_id"
    interface = IGetChassisID
    cache = True
    always_prefer = "S"

    rx_mac = re.compile(r"^\s+(MAC|MAC\s+address):\s+(?P<mac>\S+)\s*\n", re.MULTILINE)

    def execute_cli(self, **kwargs):
        mac = self.cli("show system environment", cached=True)
        match = self.rx_mac.search(mac)
        if not match:
            raise NotImplementedError
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}

    def execute_snmp(self, **kwargs):
        mac = self.snmp.get("1.3.6.1.4.1.35265.1.209.1.1.4.0", cached=True)
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
