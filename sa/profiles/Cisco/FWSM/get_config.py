# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Cisco.FWSM.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Cisco.FWSM.get_config"
    interface = IGetConfig
=======
##----------------------------------------------------------------------
## Cisco.FWSM.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig


class Script(noc.sa.script.Script):
    name = "Cisco.FWSM.get_config"
    implements = [IGetConfig]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        if self.access_profile.path:
            context = self.access_profile.path
            if context.startswith("/"):
                context = context[1:]
            self.cli("changeto context %s" % context)
        self.cli("terminal pager 0")
        config = self.cli("show running-config")
        return self.cleaned_config(config)
