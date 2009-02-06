# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Protei.MediaGateway.get_config"
    implements=[IGetConfig]
    def execute(self):
        self.cli("cd /usr/protei/CLI/Client")
        self.cli("./clip")
        for i in range(5):
            r=self.cli("end")
            if "parent." in r:
                break
        self.cli("show-recursive")
        config=self.cli("")
        return self.cleaned_config(config)
