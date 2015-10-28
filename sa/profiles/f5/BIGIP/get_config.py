# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "f5.BIGIP.get_config"
    interface = IGetConfig
    CLI_TIMEOUT = 60

    def execute(self):
        config = self.cli("list")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
