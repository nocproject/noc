# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## InfiNet.WANFlexX.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("config show")
        return self.cleaned_config(config)
