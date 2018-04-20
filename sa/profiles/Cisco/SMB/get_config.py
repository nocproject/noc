# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Cisco.SMB.get_config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Cisco.SMB.get_config"
    interface = IGetConfig

    def execute(self):
        config = self.cli("show running-config")
=======
##----------------------------------------------------------------------
## Cisco.SMB.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig

class Script(NOCScript):
    name="Cisco.SMB.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show running-config")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # config=self.strip_first_lines(config,4)
        return self.cleaned_config(config)
