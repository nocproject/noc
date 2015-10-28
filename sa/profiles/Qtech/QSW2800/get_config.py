# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW2800.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Qtech.QSW2800.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
        return self.cleaned_config(config)
