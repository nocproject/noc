# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "SKS.SKS.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
        try:
            i = config.index('!')
            config = config[i:]
        except ValueError:
            pass
        return self.cleaned_config(config)
