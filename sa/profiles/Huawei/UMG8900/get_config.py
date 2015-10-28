# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Huawei.UMG8900.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("dsp cfg;")
        return self.cleaned_config(config)
