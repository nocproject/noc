# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Huawei.VRP.get_config"
    interface = IGetConfig

<<<<<<< HEAD
    def execute(self):
        self.cli("undo terminal monitor")
        config = self.cli("display current-configuration")
        config = self.profile.clean_spaces(config)
=======

class Script(noc.sa.script.Script):
    name = "Huawei.VRP.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("display current-configuration")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return self.cleaned_config(config)
