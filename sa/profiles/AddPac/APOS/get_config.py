# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AddPac.APOS.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="AddPac.APOS.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show running-config")
        config=self.strip_first_lines(config,3)
        return self.cleaned_config(config)
