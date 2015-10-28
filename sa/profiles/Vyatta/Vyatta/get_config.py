# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vyatta.Vyatta.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig

class Script(BaseScript):
    name="Vyatta.Vyatta.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show configuration")
        return self.cleaned_config(config)
    
