# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.MA5600T.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Huawei.MA5600T.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("display saved-configuration")
        return self.cleaned_config(config)
