# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.FWSM.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Cisco.FWSM.get_config"
    interface = IGetConfig

    def execute(self):
        if self.access_profile.path:
            context = self.access_profile.path
            if context.startswith("/"):
                context = context[1:]
            self.cli("changeto context %s" % context)
        self.cli("terminal pager 0")
        config = self.cli("show running-config")
        return self.cleaned_config(config)
