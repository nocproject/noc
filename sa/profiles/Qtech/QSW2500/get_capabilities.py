# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2500.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Qtech.QSW2500.get_capabilities"

    rx_lldp = re.compile(r"LLDP enable status:\s+enable")

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp local config")
        return bool(self.rx_lldp.search(cmd))
