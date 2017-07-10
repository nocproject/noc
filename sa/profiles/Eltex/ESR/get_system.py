# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_system
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Eltex.ESR.get_system"
    cache = True
    interface = IGetConfig

    def execute(self):
        return self.cli("show system", cached=True)
