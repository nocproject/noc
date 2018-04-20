# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("export")
=======
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("export")
        config = self.cli("export")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return self.cleaned_config(config)
