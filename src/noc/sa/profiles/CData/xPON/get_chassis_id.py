# ---------------------------------------------------------------------
# CData.xPON.get_chassis_id
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
    name = "CData.xPON.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^\s+Device MAC address\s+: (?P<mac>\S+)\n", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show device", cached=True)
        match = self.rx_mac.search(v)
        if match:
            mac = match.group("mac")
            return {"first_chassis_mac": mac, "last_chassis_mac": mac}
        raise self.NotSupportedError()
