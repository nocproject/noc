# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ZTE.ZXR10.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "ZTE.ZXR10.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
