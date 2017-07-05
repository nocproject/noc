# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NSCComm.LPOS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


import re
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "NSCComm.LPOS.get_config"
    interface = IGetConfig

    def execute(self):
        return self.cleaned_config(self.cli("show cfg.sys"))
