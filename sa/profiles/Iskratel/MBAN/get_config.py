# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MBAN.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Iskratel.MBAN.get_config"
    interface = IGetConfig

    def execute(self):
        try:
            config = self.cli("show system config detail")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        return self.cleaned_config(config)
