# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Alstec.24xx.get_config"
    interface = IGetConfig
    cache = True

    rx_remove = re.compile(
        r"^!System Up Time.+\n!Current SNTP Synchronized Time.+\n",
        re.MULTILINE)

    def execute(self):
        config = self.cli("show running-config", cached=True)
        config = self.rx_remove.sub("", config)
        return self.cleaned_config(config)
