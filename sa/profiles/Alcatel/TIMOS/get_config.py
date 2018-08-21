# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.TIMOS.get_config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Alcatel.TIMOS.get_config"
    interface = IGetConfig

    def execute_cli(self):
        conf = ""
        try:
            conf = self.cli("admin display")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        conf = self.strip_first_lines(conf, 6)
        conf = self.cleaned_config(conf)
        configs = conf

        try:
            conf = self.cli("show bof")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        conf = self.cleaned_config(conf)
        configs += conf

        if not self.match_version(version__startswith=r"B-4"):
            try:
                self.cli("configure li")
            except self.CLISyntaxError:
                raise self.NotSupportedError()
            conf = self.cli("info")
            self.cli("exit")
            conf = self.cleaned_config(conf)
            configs += conf

        return configs
