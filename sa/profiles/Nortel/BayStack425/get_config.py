# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Nortel.BayStack425.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Nortel.BayStack425.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show run")
        return self.cleaned_config(config)
