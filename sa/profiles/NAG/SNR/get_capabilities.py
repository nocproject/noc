# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NAG.SNR.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.lib.text import parse_table
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "NAG.SNR.get_capabilities"

    rx_lldp_en = re.compile(r"LLDP has been enabled globally?")

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled on SNR
        """
        cmd = self.cli("show lldp", ignore_errors=True)
        return self.rx_lldp_en.search(cmd) is not None
