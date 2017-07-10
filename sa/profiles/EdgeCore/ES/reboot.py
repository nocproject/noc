# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# EdgeCore.ES.reboot
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.ireboot import IReboot


class Script(BaseScript):
    name = "EdgeCore.ES.reboot"
    interface = IReboot

    def execute(self):
        self.cli("reload \ny", nowait=True)
