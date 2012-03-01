# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NSN.hiX56xx.get_config
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "NSN.hiX56xx.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("show running-config")
        config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)
