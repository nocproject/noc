# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.SANOS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Cisco.SANOS.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
        return self.cleaned_config(config)
