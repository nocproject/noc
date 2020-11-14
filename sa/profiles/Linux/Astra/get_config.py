# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.Astra.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from noc.core.script.base import BaseScript

# NOC modules
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Linux.Astra.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        config = ""
        sstring = "-----BEGIN CONFIG BLOCK-----"
        estring = "-----END CONFIG BLOCK-----"
        clicommands = [
            "dpkg --get-selections | sort",
            "cat /etc/fstab",
            "systemctl --all --no-pager",
        ]
        for command in clicommands:
            config = config + (sstring + "\n" + self.cli(command) + estring + "\n")

        return config
