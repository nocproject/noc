# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ubiquiti.AirOS.get_version
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
    name = "Ubiquiti.AirOS.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile(r"^\S+\.v(?P<version>[^@]+)$")

    def execute_cli(self):
        # Replace # with @ to prevent prompt matching
        v = self.cli("cat /etc/version").strip()
        v_match = self.rx_version.search(v)
        board = self.cli("grep board.name /etc/board.info").strip()
        board = board.split("=", 1)[1].strip()
        return {"vendor": "Ubiquiti", "platform": board, "version": v_match.group("version")}

    def execute_snmp(self):
        try:
            platform = self.snmp.get("1.2.840.10036.3.1.2.1.3.5")
            version = self.snmp.get("1.2.840.10036.3.1.2.1.4.5")
            return {"vendor": "Ubiquiti", "platform": platform, "version": version}
        except self.snmp.TimeOutError:
            raise self.UnexpectedResultError
