# ---------------------------------------------------------------------
# DCN.DCWL.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "DCN.DCWL.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self):
        r = []
        d = self.cli("get system detail", cached=True)
        for line in d.splitlines():
            r = line.split(" ", 1)
            if r[0] == "base-mac":
                mac = r[1].strip()
        return [{"first_chassis_mac": mac, "last_chassis_mac": mac}]
