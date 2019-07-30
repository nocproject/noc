# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.RG.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Eltex.RG.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        try:
            config = self.cli("tail -n +1 /tmp/etc/config/cert/* /tmp/etc/config/*")
        except self.CLISyntaxError:
            raise self.NotSupportedError("Permission denied")
        return self.cleaned_config(config)
