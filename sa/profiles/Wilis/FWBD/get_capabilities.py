# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RT-BS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Rotek.RT-BS.get_capabilities"
    cache = True

    # def execute_platform(self, caps):
    # if self.match_version(platform__regex="^WILI*"):
    # caps["CPE | AP"] = True
