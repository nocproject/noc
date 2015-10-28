# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.GbE2.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "HP.GbE2.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("/cfg/dump")
        self.cli("/")
        return self.cleaned_config(config)
