# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "IRE-Polus.Horizon.get_capabilities"

    def execute_platform_cli(self, caps):
        crate, cu_slot = self.profile.get_cu_slot(self)
        caps["IRE-Polus | ControlUnit | Location"] = f"{crate}/{cu_slot}"
