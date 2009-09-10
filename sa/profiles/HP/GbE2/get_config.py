# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.GbE2.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="HP.GbE2.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("/cfg/dump")
        self.cli("/")
        return self.cleaned_config(config)
