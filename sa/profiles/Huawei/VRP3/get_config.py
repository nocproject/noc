# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.get_config
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
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

    def execute(self):
        with self.configure():
            config = self.cli("show running-config")
            config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)
