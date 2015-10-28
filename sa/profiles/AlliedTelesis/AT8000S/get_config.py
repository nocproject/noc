# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_config
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
    name = "AlliedTelesis.AT8000S.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
        return self.cleaned_config(config)
