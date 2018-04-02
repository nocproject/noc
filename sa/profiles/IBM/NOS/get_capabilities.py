# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IBM.NOS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "IBM.NOS.get_capabilities"

    rx_lldp = re.compile(
        r"LLDP setting\:\s+(?P<lldp>\w+)\s+", re.MULTILINE
    )

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp | include setting")
        match = self.rx_lldp.search(r)
        return match.group("lldp") == "On"

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled
        """
        r = self.cli("show spanning-tree")
        if ("Spanning Tree is shut down" in r):
            return False
        return True
