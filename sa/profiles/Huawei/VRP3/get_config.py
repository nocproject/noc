# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Huawei.VRP3.get_config
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Huawei.VRP3.get_config"
    interface = IGetConfig
=======
##----------------------------------------------------------------------
## Huawei.VRP3.get_config
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "Huawei.VRP3.get_config"
    implements = [IGetConfig]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        self.cli("no monitor")
        with self.configure():
<<<<<<< HEAD
            try:
                config = self.cli("show running-config")
            except self.CLISyntaxError:
                # MA5600 V100R011(MA5605) Version
                raise self.NotSupportedError()
=======
            config = self.cli("show running-config")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)
