# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Aruba.ArubaOS.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Aruba.ArubaOS.get_config"
    interface = IGetConfig

    def execute(self):
        v = self.cli("show running-config")
        if v.startswith("Building "):
            # Strip "Building configuration\n\n"
            v = self.strip_first_lines(v, 2)
        return v
