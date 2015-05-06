# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.reboot
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.ireboot import IReboot


class Script(NOCScript):
    name = "Juniper.JUNOS.reboot"
    implements = [IReboot]

    def execute(self):
        self.cli("request system reboot")
