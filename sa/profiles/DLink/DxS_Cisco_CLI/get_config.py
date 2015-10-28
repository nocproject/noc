# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
        config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)
