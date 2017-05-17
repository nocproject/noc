# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.get_config
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Huawei.VRP3.get_config"
    interface = IGetConfig

    def execute(self):
        self.cli("no monitor")
        with self.configure():
            try:
                config = self.cli("show running-config")
            except self.CLISyntaxError:
                # MA5600 V100R011(MA5605) Version
                raise self.NotSupportedError()
            config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)
