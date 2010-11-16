# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3xxx.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
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
        v=self.scripts.get_version()
        p=v["platform"]
        if "3612" in p or "3627" in p or "3650" in p:
            config=self.cli("show config active")
        elif "3100" in p:
            config=self.cli("show configuration running")
        else:
            config=self.cli("show config current_config")
        return self.cleaned_config(config)
