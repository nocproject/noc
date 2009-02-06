# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Juniper.JUNOS.get_config"
    implements=[IGetConfig]
    def execute(self):
        self.cli("set cli screen-length 0")
        config=self.cli("show configuration")
        return self.cleaned_config(config)
