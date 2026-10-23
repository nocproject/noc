# ---------------------------------------------------------------------
# Huawei.VRP3.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Huawei.VRP3.get_chassis_id"
    interface = IGetChassisID
    rx_mac = re.compile(r"^\s*MAC address:\s+(?P<mac>\S+)")

    def execute_cli(self, **kwargs):
        try:
            match = self.re_search(self.rx_mac, self.cli("show atmlan mac-address"))
        except self.CLISyntaxError:
            raise NotImplementedError
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
