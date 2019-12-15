# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.ZyNOS.get_capabilities_ex
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
    name = "Zyxel.ZyNOS.get_capabilities"

    rx_lldp_active = re.compile(r"Active\s*:\s*Yes", re.MULTILINE | re.IGNORECASE)
    rx_stp_active = re.compile(r"Uptime\s*:\s*\d+", re.MULTILINE | re.IGNORECASE)

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp config")
        return bool(self.rx_lldp_active.search(r))

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled
        """
        r = self.cli("show spanning-tree config")
        return bool(self.rx_stp_active.search(r))

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has oam enabled
        """
        try:
            r = self.scripts.get_oam_status()
        except Exception:
            r = False
        return bool(r)
