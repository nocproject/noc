# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.7302.get_config
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Alcatel.7302.get_config"
    interface = IGetConfig
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    CLI_TIMEOUT = 600

    def execute(self):
        self.cli("environment inhibit-alarms mode batch terminal-timeout timeout:30")
        config = self.cli("info configure flat")
        return self.cleaned_config(config)
