# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "BDCOM.xPON.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show configuration")
        return self.cleaned_config(config)
