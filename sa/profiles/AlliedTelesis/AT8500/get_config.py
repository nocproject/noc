# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8500.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "AlliedTelesis.AT8500.get_config"
    interface = IGetConfig

    def execute(self):
        #self.cli("terminal datadump")
        config = self.cli("show config dynamic")
        return self.cleaned_config(config)
