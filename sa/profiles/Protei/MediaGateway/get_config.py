# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Protei.MediaGateway.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        self.cli("cd /usr/protei/CLI/Client")
        self.cli("./clip")
        for i in range(5):
            r = self.cli("end")
            if "parent." in r:
                break
        self.cli("show-recursive")
        config = self.cli("")
        return self.cleaned_config(config)
