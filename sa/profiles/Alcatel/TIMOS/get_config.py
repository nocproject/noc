# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.TIMOS.get_config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Alcatel.TIMOS.get_config"
    interface = IGetConfig
=======
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
    name = "Alcatel.TIMOS.get_config"
    implements = [IGetConfig]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
<<<<<<< HEAD
        self.cli("configure li")
        conf['config'] = self.cli("info")
        conf['config'] = self.cleaned_config(conf['config'])
        self.cli("exit")
        configs.append(conf)

        return configs
=======
        conf['config'] = self.cli("configure li")
        conf['config'] = self.cli("info")
        conf['config'] = self.cleaned_config(conf['config'])
        configs.append(conf)

        return configs

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
