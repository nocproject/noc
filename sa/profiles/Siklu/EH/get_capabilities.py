# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Siklu.EH.get_capabilities"

    rx_lldp = re.compile(r"admin\s+: rx-tx")
    rx_oam = re.compile(r"admin\s+: enabled")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp")
        return self.rx_lldp.search(cmd) is not None

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has oam enabled
        """
        cmd = self.cli("show link-oam")
        return self.rx_oam.search(cmd) is not None
