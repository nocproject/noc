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
    cache = True

    rx_lldp = re.compile(r"^\s*\d+/\d+\s+Rx \+ Tx\s+", re.MULTILINE)
    rx_udld = re.compile("Global UDLD Status\s*:\s*(?P<status>\S+)")

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("show lldp config")
        return self.rx_lldp.search(cmd) is not None

    @false_on_cli_error
    def has_udld(self):
        """
        Check box has UDLD enabled
        """
        r = self.cli("show udld configuration")
        match = self.rx_udld.search(r)
        return match and match.group("status") == "enabled"

    @false_on_cli_error
    def has_stack(self):
        """
        Check stack members
        :return:
        """
        v = self.cli("show module")
        r = [l for l in v.splitlines() if "NI-" in l]
        return int(r[-1].split()[0].split("-")[-1])

    def execute_platform(self, caps):
        caps["Stack | Members"] = self.has_stack() if self.has_stack() else 0
