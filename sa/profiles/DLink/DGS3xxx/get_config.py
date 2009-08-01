# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3xxx.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="DLink.DGS3xxx.get_config"
    implements=[IGetConfig]
    def execute(self):
        self.cli("disable clipaging")
        v=self.scripts.get_version()
        if "3612" in v["platform"]:
            config=self.cli("show config active")
        elif "3100" in v["platform"]:
            config=self.cli("show configuration running")
        else:
            config=self.cli("show config current_config")
        return self.cleaned_config(config)
