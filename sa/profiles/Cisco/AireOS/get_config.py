# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.AireOS.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Cisco.AireOS.get_config"
    interface = IGetConfig

    def execute(self):
        version = self.scripts.get_version()["version"]
        v = int(version.split(".")[0])
        if v >= 5:
            config = self.cli("show run-config commands")
        else:
            config = self.cli("show running-config")
        return self.cleaned_config(config)
