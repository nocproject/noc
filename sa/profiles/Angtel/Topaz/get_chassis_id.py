# ---------------------------------------------------------------------
# Angtel.Topaz.get_chassis_id
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
    name = "Angtel.Topaz.get_chassis_id"
    cache = True
    interface = IGetChassisID

    always_prefer = "S"

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)

    def execute_cli(self):
        match = self.rx_mac.search(self.cli("show system", cached=True))
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
