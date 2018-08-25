# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DCN.DCWS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript, false_on_cli_error


class Script(BaseScript):
    name = "DCN.DCWS.get_capabilities"
    cache = True

    def execute_platform_cli(self, caps):
        if self.match_version(platform__regex="^DCWS*"):
            caps["CPE | Controller"] = True

    def execute_platform_snmp(self, caps):
        if self.match_version(platform__regex="^DCWS*"):
            caps["CPE | Controller"] = True
