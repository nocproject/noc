# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ubiquiti.AirOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Ubiquiti.AirOS.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile("^\S+\.v(?P<version>[^@]+)$")

    def execute(self):
        # Replace # with @ to prevent prompt matching
        v = self.cli("cat /etc/version").strip()
        v_match = self.rx_version.search(v)
        board = self.cli("grep board.name /etc/board.info").strip()
        board = board.split("=", 1)[1].strip()
        return {
            "vendor": "Ubiquiti",
            "platform": board,
            "version": v_match.group("version")
        }
