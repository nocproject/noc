# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.Openwrt.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Linux.Openwrt.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        config = ""
        sstring = "-----BEGIN CONFIG BLOCK-----"
        estring = "-----END CONFIG BLOCK-----"
        clicommands = ["opkg list-installed | sort", "cat /etc/mfstab"]
        for command in clicommands:
            config = config + (sstring + "\n" + self.cli(command) + estring + "\n")

        return config
