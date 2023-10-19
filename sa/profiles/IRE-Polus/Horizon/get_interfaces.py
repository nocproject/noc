# ----------------------------------------------------------------------
# IRE-Polus.Horizon..get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


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
        cu_params = self.profile.parse_params(cu_params["params"])
        for _, p in cu_params.items():
            if p.component_type != "Port":
                continue
            if p.component not in r:
                r[p.component] = {
                    "type": "physical",
                    "name": p.component,
                    "admin_status": False,
                    "oper_status": False,
                    "hints": ["noc::interface::role::uplink"],
                    "subinterfaces": [],
                }
            if p.name == "Mode":
                r[p.component]["oper_status"] = p.value != "Unknown"
            if p.name == "SetState":
                r[p.component]["admin_status"] = p.value == "IS"

        return [{"interfaces": list(r.values())}]
