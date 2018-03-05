# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MSAN.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Iskratel.MSAN.get_config"
    interface = IGetConfig

    def execute(self):
        try:
            config = self.cli("show running-config")
        except self.CLISyntaxError:
            # Iskratel SGR Not clearing command line when SyntaxError
            self.cli("\x1b[B")
            raise self.NotSupportedError()
        return self.cleaned_config(config)
