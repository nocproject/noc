# ----------------------------------------------------------------------
# IRE-Polus.Horizon..get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from .profile import Component


class Script(BaseScript):
    name = "IRE-Polus.Horizon.get_interfaces"
    interface = IGetInterfaces

    def execute(self, **kwargs):
        r = {}
        crate, cu_slot = self.profile.get_cu_slot(self)
        cu_params = self.http.get(
            f"/api/devices/params?crateId={crate}&slotNumber={cu_slot}&fields=name,value,description",
            json=True,
            cached=True,
        )
        components = Component.from_params(cu_params["params"])
        for c_name, c in components.items():
            if not c_name.startswith("Port"):
                continue
            if c_name not in r:
                r[c_name] = {
                    "type": "physical",
                    "name": c_name,
                    "admin_status": False,
                    "oper_status": False,
                    "hints": ["noc::interface::role::uplink"],
                    "subinterfaces": [],
                }
            # if p.name == "Mode":
            #     r[p.component]["oper_status"] = p.value != "Unknown"
            # if p.name == "SetState":
            #    r[p.component]["admin_status"] = p.value == "IS"

        return [{"interfaces": list(r.values())}]
