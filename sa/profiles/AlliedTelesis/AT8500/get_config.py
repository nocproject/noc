# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlliedTelesis.AT8500.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "AlliedTelesis.AT8500.get_config"
    interface = IGetConfig

    def execute(self):
        # self.cli("terminal datadump")
=======
##----------------------------------------------------------------------
## AlliedTelesis.AT8500.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "AlliedTelesis.AT8500.get_config"
    implements = [IGetConfig]

    def execute(self):
        #self.cli("terminal datadump")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        config = self.cli("show config dynamic")
        return self.cleaned_config(config)
