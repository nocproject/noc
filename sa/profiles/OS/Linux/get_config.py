# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OS.Linux.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "OS.Linux.get_config"
    interface = IGetConfig

    always_prefer = "С"

    def execute(self, **kwargs):
        config = ""
        sstring = "-----BEGIN CONFIG BLOCK-----"
        estring = "-----END CONFIG BLOCK-----"
        clicommands = [
            "rpm -qa | sort",
            "cat /etc/fstab",
            'systemctl --all --no-pager | grep -v "session-.*Session"',
        ]
        for command in clicommands:
            config = config + (sstring + "\n" + self.cli(command) + estring + "\n")
        return config
