# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UPVEL.UP.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "UPVEL.UP.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
        # Remove "Building configuration..." line
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
