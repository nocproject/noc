# ---------------------------------------------------------------------
# NSCComm.LPOS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "NSCComm.LPOS.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        v = self.cli("show cfg.sys")
        return self.cleaned_config(v)
