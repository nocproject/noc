# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.WLC.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Cisco.WLC.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show run-config commands")
        return self.cleaned_config(config)
