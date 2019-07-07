# -*- coding: utf-8 -*-
__author__ = "FeNikS"
# ---------------------------------------------------------------------
# Sencore.Probe.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Sencore.Probe.get_config"
    interface = IGetConfig

    suffixes = ["/probe/status", "/probe/generaldata?&&", "/probe/etrdata?&&"]

    def execute(self):
        result = ['<?xml version="1.0"?>\n<Root>']

        for suffix in self.suffixes:
            data = self.http.get(suffix)
            data = data.replace('<?xml version="1.0"?>', "")
            result.append(data)
        result.append("</Root>")
        config = "\n".join(result)

        return self.cleaned_config(config)
