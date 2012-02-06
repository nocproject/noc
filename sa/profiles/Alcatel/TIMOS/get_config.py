# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.TIMOS.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "Alcatel.TIMOS.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("admin display")
        config = self.strip_first_lines(config, 6)
        return self.cleaned_config(config)
