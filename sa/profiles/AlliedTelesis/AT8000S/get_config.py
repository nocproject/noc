# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="AlliedTelesis.AT8000S.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show running-config")
        return self.cleaned_config(config)
