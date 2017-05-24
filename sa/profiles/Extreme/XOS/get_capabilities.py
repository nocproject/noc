# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Extreme.XOS.get_capabilities"

    rx_lldp = re.compile(r"^\s*\d+\s+Enabled\s+Enabled", re.MULTILINE)
    rx_cdp = re.compile(r"^\s*CDP \S+ enabled ports\s+:\s+\d+", re.MULTILINE)

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp")
        return self.rx_lldp.search(cmd) is not None

    @false_on_cli_error
    def has_cdp(self):
        """
        Check box has CDP enabled
        """
        cmd = self.cli("show cdp")
        return self.rx_cdp.search(cmd) is not None
