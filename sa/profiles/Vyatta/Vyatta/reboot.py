# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vyatta.Vyatta.reboot
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.ireboot import IReboot


class Script(NOCScript):
    name = "Vyatta.Vyatta.reboot"
    implements = [IReboot]

    def execute(self):
        self.cli("reboot")
