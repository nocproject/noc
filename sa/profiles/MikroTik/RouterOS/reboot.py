# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# MikroTik.RouterOS.reboot
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.ireboot import IReboot


class Script(BaseScript):
    name = "MikroTik.RouterOS.reboot"
    interface = IReboot
=======
##----------------------------------------------------------------------
## MikroTik.RouterOS.reboot
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.ireboot import IReboot


class Script(NOCScript):
    name = "MikroTik.RouterOS.reboot"
    implements = [IReboot]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        self.cli("/system reboot", nowait=True)
