# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.ASA.get_capabilities_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Cisco.ASA.get_capabilities"

    sec_mode = re.compile(r".+?: (?P<mode>multiple|single|noconfirm)\s+", re.MULTILINE | re.DOTALL)

    @false_on_cli_error
    def execute_platform(self, caps):
        caps["Cisco | ASA | Security | Context | Mode"] = "nosupport"
        v = self.cli("show mode")
        if "Invalid input detected at" not in v:
            match = self.re_search(self.sec_mode, v)
            sec_mode = match.group("mode")
            self.logger.debug('Mode {0}'.format(sec_mode))
            caps["Cisco | ASA | Security | Context | Mode"] = sec_mode
