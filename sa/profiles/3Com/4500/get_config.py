# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.4500.get_config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "3Com.4500.get_config"
    interface = IGetConfig
    cache = True

    def execute_cli(self, **kwargs):
        config = self.cli("display current-configuration", cached=True)
        return self.cleaned_config(config)
