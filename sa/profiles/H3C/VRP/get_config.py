# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## H3C.VRP.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "H3C.VRP.get_config"
    interface = IGetConfig

    def execute(self):
        self.cli("undo terminal monitor")
        config = self.cli("display current-configuration")
        config = self.profile.clean_spaces(config)
        return self.cleaned_config(config)
