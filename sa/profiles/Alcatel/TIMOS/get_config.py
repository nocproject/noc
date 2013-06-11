# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.TIMOS.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    TIMEOUT = 850
    name = "Alcatel.TIMOS.get_config"
    implements = [IGetConfig]

    def execute(self):
        configs = []

        conf = {}
        conf['name'] = "admin display"
        conf['config'] = self.cli("admin display")
        conf['config'] = self.strip_first_lines(conf['config'], 6)
        conf['config'] = self.cleaned_config(conf['config'])
        configs.append(conf)

        conf = {}
        conf['name'] = "show bof"
        conf['config'] = self.cli("show bof")
        conf['config'] = self.cleaned_config(conf['config'])
        configs.append(conf)

        conf = {}
        conf['name'] = "li"
        conf['config'] = self.cli("configure li")
        conf['config'] = self.cli("info")
        conf['config'] = self.cleaned_config(conf['config'])
        configs.append(conf)

        return configs

