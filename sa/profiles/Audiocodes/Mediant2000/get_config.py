# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Audiocodes.Mediant2000.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        self.cli("conf")
        config = self.cli("cf get")
        return self.cleaned_config(config)

    def execute_http(self):
        config = self.http.get("/FS/BOARD.ini")
        return self.cleaned_config(config)
