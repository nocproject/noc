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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "AlliedTelesis.AT8000S.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("show running-config")
        return self.cleaned_config(config)
