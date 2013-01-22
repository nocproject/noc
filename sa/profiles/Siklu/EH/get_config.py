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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "Siklu.EH.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("copy running-configuration display")
        return self.cleaned_config(config)
