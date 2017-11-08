# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_switch
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "DLink.DxS.get_switch"
    cache = True
    interface = IGetConfig

    def execute(self):
        return self.cli("show switch", cached=True)
