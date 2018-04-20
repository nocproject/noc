# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC.SAE.get_activator_info
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetActivatorInfo


class Script(NOCScript):
    name = "NOC.SAE.get_activator_info"
    implements = [IGetActivatorInfo]

    def execute(self):
        r = self.sae.get_activator_status()
        self.sae.refresh_activator_status()
        return r
