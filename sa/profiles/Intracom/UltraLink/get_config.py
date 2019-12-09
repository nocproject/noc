# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Intracom.UltraLink.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Intracom.UltraLink.get_config"
    interface = IGetConfig

    def execute_cli(self, policy="r", **kwargs):
        config = self.cli("config show current")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
