# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.TIMOS.get_capabilities_ex
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
    name = "Alcatel.TIMOS.get_capabilities"

    CHECK_SNMP_GET = {
        "BRAS | IPoE": "1.3.6.1.4.1.6527.3.1.2.33.1.107.1.65.1"
    }
    rx_lldp = re.compile(r"Admin Enabled\s+: True")

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show system lldp | match Admin")
        return self.rx_lldp.search(cmd) is not None
