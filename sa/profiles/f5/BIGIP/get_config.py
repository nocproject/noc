# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# f5.BIGIP.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "f5.BIGIP.get_config"
    interface = IGetConfig
=======
##----------------------------------------------------------------------
## f5.BIGIP.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "f5.BIGIP.get_config"
    implements = [IGetConfig]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    CLI_TIMEOUT = 60

    def execute(self):
        config = self.cli("list")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
