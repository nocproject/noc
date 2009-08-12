# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Force10.FTOS.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show running-config | no-more")
        config=self.strip_first_lines(config,1)
        return self.cleaned_config(config)
