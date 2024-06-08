# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_uptime
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetuptime import IGetUptime
from .profile import PolusParam


class Script(BaseScript):
    """
    Returns system uptime in seconds
    """

    name = "IRE-Polus.Horizon.get_uptime"
    interface = IGetUptime
    requires = []

    def execute(self):
        crate, cu_slot = self.profile.get_cu_slot(self)
        v = self.http.get(
            f"/api/devices/params?crateId={crate}&slotNumber={cu_slot}&names=Time&fields=name,value,description",
            json=True,
        )
        for p in v["params"]:
            p = PolusParam.from_code(**p)
            if p.name == "Time":
                return float(p.value)
        return None
