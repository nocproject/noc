# ---------------------------------------------------------------------
# NSCComm.LPOS.get_chassis_id
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
    name = "NSCComm.LPOS.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^Physical Address\s+: (?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        v = self.cli("stats", cached=True)
        match = self.rx_mac.search(v)
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
