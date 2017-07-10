# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3.get_capabilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "3Com.SuperStack3.get_capabilities"

    rx_stp = re.compile(r"stpState\s*:\s+disable")

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("bridge summary")
        return self.rx_stp.search(cmd) is None
