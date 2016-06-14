# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_capabilities
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
    name = "Alcatel.AOS.get_capabilities"

    rx_lldp = re.compile(r"LLDP Mode\s+= Bridge Mode")
    rx_udld = re.compile("Global UDLD Status\s*:\s*(?P<status>\S+)")

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("show lldp LOCAL-SYSTEM")
        return self.rx_lldp.search(cmd) is not None

    @false_on_cli_error
    def has_udld(self):
        """
        Check box has UDLD enabled
        """
        r = self.cli("show udld configuration")
        match = self.rx_udld.search(r)
        return match and match.group("status") == "enabled"
