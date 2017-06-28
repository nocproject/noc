# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Eltex.MA4000.get_config"
    interface = IGetConfig

    def execute(self):
        conf = self.cli("show running-config")
        return self.cleaned_config(conf)
