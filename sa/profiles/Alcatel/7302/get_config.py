# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7302.get_config
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(NOCScript):
    name = "Alcatel.7302.get_config"
    implements = [IGetConfig]

    CLI_TIMEOUT = 600

    def execute(self):
        self.cli("environment inhibit-alarms mode batch terminal-timeout timeout:30")
        config = self.cli("info configure flat")
        return self.cleaned_config(config)
