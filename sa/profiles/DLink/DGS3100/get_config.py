# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "DLink.DGS3100.get_config"
    interface = IGetConfig

    def execute(self):
        return self.cleaned_config(self.cli("show configuration running"))
