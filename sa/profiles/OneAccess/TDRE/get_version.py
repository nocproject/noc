# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OneAccess.TDRE.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "OneAccess.TDRE.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r'sysDescr = "(?P<platform>\S+).+?(?P<version>\S+)\s\S+\s\S+"$', re.MULTILINE
    )

    def execute(self):
        self.cli("SELGRP Status")
        match = self.rx_ver.search(self.cli("GET /"))
        return {
            "vendor": "OneAccess",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
