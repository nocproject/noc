# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8500.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
#from __future__ import with_statement
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="AlliedTelesis.AT8500.get_config"
    implements=[IGetConfig]
    def execute(self):
        #self.cli("terminal datadump")
        config=self.cli("show config dynamic")
        return self.cleaned_config(config)
