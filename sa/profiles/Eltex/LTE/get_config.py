# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTE.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Eltex.LTE.get_config"
    interface = IGetConfig

    def execute(self):
        with self.profile.switch(self):
            conf = self.cli("show running-config")

        for i in ['0', '1', '2', '3']:
            conf = conf + self.cli("olt " + i)
            for j in [
                'ipmc', 'layer3', 'network', 'ports', 'pppoe', 'traffic'
            ]:
                conf = conf + "\n" + self.cli("show config " + j)
            self.cli("exit")

        return self.cleaned_config(conf)
