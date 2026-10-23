# ---------------------------------------------------------------------
# Force10.FTOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Force10.FTOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self, **kwargs):
        if self.is_s:
            return self.execute_s()
        return self.execute_other()

    # S-Series
    rx_system_id = re.compile(r"Stack MAC\s+:\s*(?P<id>\S+)", re.IGNORECASE | re.MULTILINE)

    def execute_s(self):
        """
        S-series
        :return:
        """
        v = self.cli("show system brief")
        match = self.re_search(self.rx_system_id, v)
        mac = match.group("id")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}

    # C/E-series
    rx_chassis_id = re.compile(r"Chassis MAC\s+:\s*(?P<id>\S+)", re.IGNORECASE | re.MULTILINE)

    def execute_other(self):
        """
        C/E-series
        :return:
        """
        v = self.cli("show chassis brief")
        match = self.re_search(self.rx_chassis_id, v)
        mac = match.group("id")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
