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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(NOCScript):
    name = "Aruba.ArubaOS.get_config"
    implements = [IGetConfig]

    def execute(self):
        v = self.cli("show running-config")
        return v
