# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "DLink.DGS3100.get_config"
    implements = [IGetConfig]
    TIMEOUT = 360

    def execute(self):
        return self.cleaned_config(self.cli("show configuration running"))
