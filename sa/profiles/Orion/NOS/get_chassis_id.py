# ---------------------------------------------------------------------
# Orion.NOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Orion.NOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute_cli(self):
        v = self.profile.get_version(self)
        r = [{"first_chassis_mac": v["mac"], "last_chassis_mac": v["mac"]}]
        if v.get("mac2") is not None:
            r += [{"first_chassis_mac": v["mac2"], "last_chassis_mac": v["mac2"]}]
        return r
