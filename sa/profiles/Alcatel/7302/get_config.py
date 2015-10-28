# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7302.get_config
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Alcatel.7302.get_config"
    interface = IGetConfig

    CLI_TIMEOUT = 600

    def execute(self):
        self.cli("environment inhibit-alarms mode batch terminal-timeout timeout:30")
        config = self.cli("info configure flat")
        return self.cleaned_config(config)
