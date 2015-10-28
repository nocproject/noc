# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Juniper.JUNOS.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show configuration")
        return self.cleaned_config(config)
