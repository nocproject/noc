# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_capabilities_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_capabilities"

    rx_active = re.compile("Active\s*:\s*Yes",
                           re.MULTILINE | re.IGNORECASE)

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp config")
        return bool(self.rx_active.search(r))
