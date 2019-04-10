# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Maipu.OS.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        self.cli("enable")
        config = self.cli("show running-config")
        return self.cleaned_config(config)
