# ---------------------------------------------------------------------
# Axis.VAPIX.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Axis.VAPIX.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self):
        macs = []
        c = self.profile.get_dict(self)
        for i in range(4):  # for future models
            mac = c.get("root.Network.eth%d.MACAddress" % i)
            if mac is not None:
                macs += [mac]
        return [{"first_chassis_mac": m, "last_chassis_mac": m} for m in sorted(macs)]
