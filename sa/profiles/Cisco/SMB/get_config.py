# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SMB.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig

class Script(NOCScript):
    name="Cisco.SMB.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show running-config")
        # config=self.strip_first_lines(config,4)
        return self.cleaned_config(config)
