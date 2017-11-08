# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.SMG.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Eltex.SMG.get_config"
    interface = IGetConfig

    def execute(self):
        conf = self.cli("sh")
        conf = self.cli("cat /etc/config/cfg.yaml")
        return self.cleaned_config(conf)
