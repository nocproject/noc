# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
## NOC modules
from noc.sa.script import NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "f5.BIGIP.get_config"
    implements = [IGetConfig]
    TIMEOUT = 300
    CLI_TIMEOUT = 60

    def execute(self):
        print self.tmsh
        with self.tmsh():
            config = self.cli("list")  # Get config
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
