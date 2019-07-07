# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Tangram.GT21.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Tangram.GT21.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        platform = "GT21"
        version = "Unknown"

        return {"vendor": "Tangram", "platform": platform, "version": version}
