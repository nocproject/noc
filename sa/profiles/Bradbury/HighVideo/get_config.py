# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Bradbury.HighVideo.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import ujson

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Bradbury.HighVideo.get_config"
    interface = IGetConfig
    TIMEOUT = 240
    CLI_TIMEOUT = 240
    SECTIONS = ["load-Servers", "load-Channels", "load-Profiles", "load-Multiplexes"]

    def execute(self, **kwargs):
        result = {}
        for section in self.SECTIONS:
            result[section] = self.http.post("/upload/", data=section, json=True, use_basic=True)
        return ujson.dumps(result, indent=2)
