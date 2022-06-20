# ----------------------------------------------------------------------
# 3Com.SuperStack3_4500.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "3Com.SuperStack3_4500.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(
        r"(?:Hardware address is|First mac address\s+:) (?P<mac>\S+)\s*$", re.MULTILINE
    )

    def execute_cli(self):
        macs = []
        try:
            v = self.cli("display device manuinfo", cached=True)
            match = self.rx_mac.search(v)
            if match:
                macs += [match.group("mac")]
        except self.CLISyntaxError:
            pass
        v = self.cli("display interface", cached=True)
        for match in self.rx_mac.finditer(v):
            if match.group("mac") not in macs:
                macs += [match.group("mac")]
        macs.sort()
        return [
            {"first_chassis_mac": f, "last_chassis_mac": t} for f, t in self.macs_to_ranges(macs)
        ]
