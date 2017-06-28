# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.7200.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Alstec.7200.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
        return self.cleaned_config(config)
