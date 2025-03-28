# ---------------------------------------------------------------------
# HP.ProCurve.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "HP.ProCurve.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"([0-9a-f]{6}-[0-9a-f]{6})", re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def execute_cli(self):
        v = self.cli("show management")
        match = self.re_search(self.rx_mac, v)
        mac = match.group(1)
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
