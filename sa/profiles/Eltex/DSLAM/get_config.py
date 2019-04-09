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
        config = ''
        try:
            for j in ['user', 'adsl', 'iptv', 'snmp', 'pppi', 'dhcp']:
                config = config + "\n" + self.cli("system show cfg file " + j)
        except self.CLISyntaxError:
            pass
        return self.cleaned_config(config)
