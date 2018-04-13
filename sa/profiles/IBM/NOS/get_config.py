# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IBM.NOS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "IBM.NOS.get_config"
    interface = IGetConfig

    def execute_cli(self):
        config = self.cli("show running-config")
        config = self.strip_first_lines(config, 2)
        return self.cleaned_config(config)
