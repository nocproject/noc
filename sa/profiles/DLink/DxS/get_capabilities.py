# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_capabilities
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
    name = "DLink.DxS.get_capabilities"

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        rx_lldp = re.compile(r"LLDP Status\s+: Enabled?")
        cmd = self.cli("show lldp")
        return rx_lldp.search(cmd) is not None
