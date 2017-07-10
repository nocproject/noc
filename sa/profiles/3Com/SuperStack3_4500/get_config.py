# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3_4500.get_config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "3Com.SuperStack3_4500.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("display current-configuration")
        return self.cleaned_config(config)
