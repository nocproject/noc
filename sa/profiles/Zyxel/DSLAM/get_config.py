# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.DSLAM.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Zyxel.DSLAM.get_config"
    interface = IGetConfig

    def execute(self):
        try:
            config = self.cli("show config-0")
        except self.CLISyntaxError:
            try:
                config = self.cli("config show all nopause")
            except self.CLISyntaxError:
                config = self.cli("config print")
        return self.cleaned_config(config)
