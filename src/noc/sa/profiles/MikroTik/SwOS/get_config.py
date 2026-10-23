# ---------------------------------------------------------------------
# MikroTik.SwOS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "MikroTik.SwOS.get_config"
    interface = IGetConfig

    def execute(self, **kwargs):
        return self.http.get("/backup.swb", cached=True, eof_mark=b"}")
        # config = self.profile.parseBrokenJson(config)
