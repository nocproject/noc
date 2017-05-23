# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ericsson.MINI_LINK.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Ericsson.MINI_LINK.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli_clean("show running-config")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
