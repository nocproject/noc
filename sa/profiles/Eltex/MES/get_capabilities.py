# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Eltex.MES.get_capabilities"

    rx_lldp = re.compile(r"LLDP state: Enabled?")

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled on Eltex
        """
        cmd = self.cli("show lldp configuration")
        return self.rx_lldp.search(cmd) is not None