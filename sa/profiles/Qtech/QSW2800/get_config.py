# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW2800.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "Qtech.QSW2800.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("show running-config")
        return self.cleaned_config(config)
