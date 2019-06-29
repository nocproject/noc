# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.Summit200.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Extreme.Summit200.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        config = self.cli("show configuration")
        return self.cleaned_config(config)
