# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.sa.script import NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name="f5.BIGIP.get_config"
    implements=[IGetConfig]
    TIMEOUT = 300
    CLI_TIMEOUT = 60
    def execute(self):
        self.cli("tmsh")  # Enter tmsh
        self.cli("modify /cli preference pager disabled")  # Disable pager
        config = self.cli("list")  # Get config
        self.cli("quit")  # Leave tmsh
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
