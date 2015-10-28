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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Zebra.Zebra.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
        config = self.strip_first_lines(config, 2)
        return self.cleaned_config(config)
