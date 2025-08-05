# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_params_crate
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlist import IGetList


class Script(BaseScript):
    name = "IRE-Polus.Horizon.get_crate_params"
    interface = IGetList

    def execute_cli(self):
        crates = self.http.get(
            "/api/crates",
            json=True,
        )
        if not crates:
            return

        crate_params_group = self.http.get(
            f"/api/crates/params/groups",
            json=True,
        )

        crate_params = self.http.get(
            f"/api/crates/params",
            json=True,
        )

        param_list = [x["name"] for x in crate_params["params"]]

        return param_list
