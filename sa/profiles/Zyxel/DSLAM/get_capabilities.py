# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.DSLAM.get_capabilities
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
    name = "Zyxel.DSLAM.get_capabilities"

    rx_stp_active = re.compile(r"status\s+:\s+enabled", re.MULTILINE)

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has stp enabled
        """
        r = self.cli("switch rstp show", cached=True)
        return bool(self.rx_stp_active.search(r))
