# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.DSLAM.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Eltex.DSLAM.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        config = ""
        try:
            if self.is_platform_MXA32 or self.is_platform_MXA64:
                for j in ["user", "adsl", "iptv", "snmp", "pppi", "dhcp"]:
                    config = config + "\n" + self.cli("system show cfg file " + j)
            elif self.is_platform_MXA24:
                for j in ["user config", "snmp config", "net settings"]:
                    config = config + "\n" + self.cli("system show " + j)
        except self.CLISyntaxError:
            pass
        return self.cleaned_config(config)
