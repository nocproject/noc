# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Siemens.HIX5630.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show running-config")
        config=self.strip_first_lines(config,3)
        return self.cleaned_config(config)
