# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Huawei.VRP.get_config"
    interface = IGetConfig

    def execute_cli(self, policy="r", **kwargs):
        self.cli("undo terminal monitor", ignore_errors=True)
        assert policy in ("r", "s")
        if policy == "s":
            config = self.cli("display saved-configuration")
        else:
            config = self.cli("display current-configuration")
        config = self.profile.clean_spaces(config)
        return self.cleaned_config(config)
