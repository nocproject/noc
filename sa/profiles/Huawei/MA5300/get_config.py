# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
## Huawei.MA5300.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Huawei.MA5300.get_config"
    interface = IGetConfig

    def execute(self):
#	self.cli("cls")
        self.cli("conf t")
        self.cli("line vty 0 3")
        self.cli("length 0")
        config = self.cli("show running-config")
        self.cli("no length")
        return self.cleaned_config(config)

