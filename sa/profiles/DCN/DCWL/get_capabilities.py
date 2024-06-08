# ---------------------------------------------------------------------
# DCN.DCWL.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "DCN.DCWL.get_capabilities"
    cache = True

    # devices does not support SNMP

    # def execute_platform(self, caps):
    # if self.match_version(platform__regex="^DCWL*"):
    # caps["CPE | AP"] = True
