# ---------------------------------------------------------------------
# Nateks.FlexGain.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Nateks.FlexGain.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"MAC Address\s+:\s*(?P<mac>\S+)")

    def execute(self):
        v = self.cli("show system information", cached=True)
        macs = sorted(self.rx_mac.findall(v))
        return [
            {"first_chassis_mac": f, "last_chassis_mac": t} for f, t in self.macs_to_ranges(macs)
        ]
