# ---------------------------------------------------------------------
# UTST.ONU.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "UTST.ONU.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac1 = re.compile(r"^(?P<mac>\S+)\s+\d+\s+(dynamic|static)\s+cpu", re.MULTILINE)
    rx_mac2 = re.compile(r"^\s+Ethernet address is\s(?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        if self.is_platform_onu208:
            cmd = self.cli("show mac")
            match = self.rx_mac1.search(cmd)
            fmac = match.group("mac")
            lmac = match.group("mac")
            return [{"first_chassis_mac": fmac, "last_chassis_mac": lmac}]
        cmd = self.cli("show interface")
        macs = sorted(self.rx_mac2.findall(cmd))
        return [
            {"first_chassis_mac": f, "last_chassis_mac": t} for f, t in self.macs_to_ranges(macs)
        ]
