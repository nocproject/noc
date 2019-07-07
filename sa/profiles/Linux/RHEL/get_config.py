# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.RHEL.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from noc.core.script.base import BaseScript

# NOC modules
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Linux.RHEL.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        config = ""
        configrpm = self.cli("rpm -qa | sort")
        configmount = self.cli("cat /etc/fstab")
        config = configrpm + "\n" + configmount
        return config
