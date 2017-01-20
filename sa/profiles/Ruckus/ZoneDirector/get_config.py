# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ruckus.ZoneDirector.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Ruckus.ZoneDirector.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show config")
        config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)