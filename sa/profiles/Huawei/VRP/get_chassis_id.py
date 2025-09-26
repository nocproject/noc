# ---------------------------------------------------------------------
# Huawei.VRP.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Huawei.VRP.get_chassis_id"
    always_prefer = "S"
    interface = IGetChassisID

    rx_mac = re.compile(r"MAC address[^:]*?:\s*(?P<id>\S+)", re.IGNORECASE | re.MULTILINE)
    rx_mac1 = re.compile(
        r"(CIST Bridge|Bridge ID)\s+:\d+\s*\.(?P<id>\S+)", re.IGNORECASE | re.MULTILINE
    )

    def execute_cli(self):
        v = self.cli("display stp", cached=True)
        match = self.rx_mac.search(v)
        if match:
            mac = match.group("id")
            return {"first_chassis_mac": mac, "last_chassis_mac": mac}
        match = self.rx_mac1.search(v)
        if match:
            mac = match.group("id")
            return {"first_chassis_mac": mac, "last_chassis_mac": mac}

        raise self.NotSupportedError()
