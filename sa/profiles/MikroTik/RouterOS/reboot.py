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

    def execute(self):
        self.cli("/system reboot", nowait=True)
