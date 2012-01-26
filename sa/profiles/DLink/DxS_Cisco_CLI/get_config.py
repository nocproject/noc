# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("show running-config")
        config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)
