# ----------------------------------------------------------------------
# NSN.TIMOS.get_config
# ----------------------------------------------------------------------
# NSN.TIMOS.get_config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "NSN.TIMOS.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        configs = []

        conf = {}
        conf["name"] = "admin display"
        conf["config"] = self.cli("admin display")
        conf["config"] = self.strip_first_lines(conf["config"], 6)
        conf["config"] = self.cleaned_config(conf["config"])
        configs.append(conf)

        conf = {}
        conf["name"] = "show bof"
        conf["config"] = self.cli("show bof")
        conf["config"] = self.cleaned_config(conf["config"])
        configs.append(conf)

        conf = {}
        conf["name"] = "li"
        # 7705 SAR-X dont have this command
        try:
            self.cli("configure li")
            conf["config"] = self.cli("info")
            conf["config"] = self.cleaned_config(conf["config"])
            self.cli("exit")
            configs.append(conf)
        except self.CLISyntaxError:
            pass

        return configs
