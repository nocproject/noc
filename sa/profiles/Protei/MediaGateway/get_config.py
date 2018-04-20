# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Protei.MediaGateway.get_config"
    interface = IGetConfig

<<<<<<< HEAD
=======

class Script(noc.sa.script.Script):
    name = "Protei.MediaGateway.get_config"
    implements = [IGetConfig]

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        self.cli("cd /usr/protei/CLI/Client")
        self.cli("./clip")
        for i in range(5):
            r = self.cli("end")
            if "parent." in r:
                break
        self.cli("show-recursive")
        config = self.cli("")
        return self.cleaned_config(config)
