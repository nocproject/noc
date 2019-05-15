# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Axis.VAPIX.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Axis.VAPIX.get_config"
    cache = True
    interface = IGetConfig

    def execute(self, **kwargs):
        return self.profile.get_list(self)
