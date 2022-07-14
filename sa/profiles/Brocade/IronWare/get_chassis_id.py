# ---------------------------------------------------------------------
# Brocade.IronWare.get_chassis_id
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
    name = "Brocade.IronWare.get_chassis_id"
    interface = IGetChassisID
    rx_mac = re.compile(
        r"([0-9a-f]{4}.[0-9a-f]{4}.[0-9a-f]{4})", re.IGNORECASE | re.MULTILINE | re.DOTALL
    )

    def execute_cli(self):
        v = self.cli("show chassis", cached=True)
        match = self.rx_mac.search(v)
        mac = match.group(1)
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
