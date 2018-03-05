# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Juniper.EX2500.get_config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Juniper.EX2500.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show active-config")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
