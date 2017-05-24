# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ruckus.ZoneDirector.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript, false_on_cli_error


class Script(BaseScript):
    name = "Ruckus.ZoneDirector.get_capabilities"
    cache = True

    def execute_platform(self, caps):
        if self.match_version(platform__regex="^ZD"):
            caps["CPE | Controller"] = True
        if self.has_snmp():
            stat = self.snmp.get("1.3.6.1.4.1.25053.1.2.1.1.1.1.30.0", cached=True)  
            if stat == 1:
                caps["CPE | Controller Status"] = "Master"
            elif stat ==2:
                caps["CPE | Controller Status"] = "Standby" 
            elif stat ==3:
                caps["CPE | Controller Status"] = "Noredundancy"
