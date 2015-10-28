# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Cisco.ASA.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("more system:running-config")
        config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)
