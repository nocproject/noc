# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve9xxx.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "HP.ProCurve9xxx.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show config")
        config = self.strip_first_lines(config, 2)
        return self.cleaned_config(config)
