# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name = "Eltex.MES.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("show running-config")
#        config = self.strip_first_lines(config,3)
        return self.cleaned_config(config)
