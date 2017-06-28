# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_capabilities
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
    name = "Iskratel.ESCOM.get_capabilities"

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("show lldp configuration")
        return "LLDP state: Enabled" in cmd

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("show spanning-tree active")
        return "  enabled  " in cmd
