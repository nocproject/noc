# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5300.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Huawei.MA5300.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
        return config
