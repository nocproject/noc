# ---------------------------------------------------------------------
# NSN.hiX56xx.get_config
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "NSN.hiX56xx.get_config"
    interface = IGetConfig

    def execute_cli(self, policy="r", **kwargs):
        assert policy in ("r", "s")
        if policy == "s":
            config = self.cli("show startup-config")
        else:
            config = self.cli("show running-config")
        config = self.strip_first_lines(config, 2)
        return self.cleaned_config(config)
