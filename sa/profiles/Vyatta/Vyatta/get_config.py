# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vyatta.Vyatta.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig

class Script(BaseScript):
    name="Vyatta.Vyatta.get_config"
    interface = IGetConfig
=======
##----------------------------------------------------------------------
## Vyatta.Vyatta.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Vyatta.Vyatta.get_config"
    implements=[IGetConfig]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        config=self.cli("show configuration")
        return self.cleaned_config(config)
    
