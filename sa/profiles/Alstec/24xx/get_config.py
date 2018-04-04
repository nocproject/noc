# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Alstec.24xx.get_config"
    interface = IGetConfig
    cache = True

    def execute(self):
        config = self.cli("show running-config", cached=True)
        return self.cleaned_config(config)
