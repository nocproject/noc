# ---------------------------------------------------------------------
# Symbol.AP.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Symbol.AP.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^Base ethernet MAC address is (?P<mac>\S+)", re.MULTILINE)

    def execute_cli(self):
        c = self.cli("show version", cached=True)
        mac = self.rx_mac.search(c).group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
