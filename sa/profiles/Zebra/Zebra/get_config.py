# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zebra.Zebra.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "Zebra.Zebra.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("show running-config")
        config = self.strip_first_lines(config, 2)
        return self.cleaned_config(config)
