# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.Comware.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig


class Script(noc.sa.script.Script):
    name = "HP.Comware.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("display current-configuration")
        return self.cleaned_config(config)