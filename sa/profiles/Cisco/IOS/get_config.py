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
    name="Cisco.IOS.get_config"
    implements=[IGetConfig]
    def execute(self):
        self.cli("terminal length 0")
        config=self.cli("show running-config")
        config=self.strip_first_lines(config,3)
        return self.cleaned_config(config)
