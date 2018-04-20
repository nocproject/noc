# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Aruba.ArubaOS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Aruba.ArubaOS.get_config"
    interface = IGetConfig
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        v = self.cli("show running-config")
        if v.startswith("Building "):
            # Strip "Building configuration\n\n"
            v = self.strip_first_lines(v, 2)
        return v
