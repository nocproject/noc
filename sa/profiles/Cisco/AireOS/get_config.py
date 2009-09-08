# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.AireOS.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Cisco.AireOS.get_config"
    implements=[IGetConfig]
    def execute(self):
        version=self.scripts.get_version()["version"]
        v=int(version.split(".")[0])
        if v>=5:
            config=self.cli("show run-config commands")
        else:
            config=self.cli("show running-config")
        return self.cleaned_config(config)
