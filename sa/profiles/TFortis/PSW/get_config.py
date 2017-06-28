# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig

class Script(BaseScript):
    name="TFortis.PSW.get_config"
    interface = IGetConfig
    def execute(self):
        self.http.post("/savesett.shtml","save=Create%20a%20file")
        config=self.http.get("/PSW_settings_backup.bak")
        return self.cleaned_config(config)
