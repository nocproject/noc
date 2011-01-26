# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOSe.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig
## Juniper.JUNOSe.get_config
class Script(NOCScript):
    name="Juniper.JUNOSe.get_config"
    implements=[IGetConfig]
    def execute(self):
        try:
            config=self.cli("show running-configuration")
        except self.CLISyntaxError:
            config=self.cli("show configuration")
        return self.cleaned_config(config)
    
