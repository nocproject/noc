# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DVG.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "DLink.DVG.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        config = self.cli("cat /tmp/etc/default/config.json\n")
        return self.cleaned_config(config)
