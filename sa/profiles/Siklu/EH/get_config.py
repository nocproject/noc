# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Siklu.EH.get_config
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
    name = "Siklu.EH.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("copy running-configuration display")
        return self.cleaned_config(config)
