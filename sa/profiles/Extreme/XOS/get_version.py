# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Extreme.XOS.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^Card type:\s+(?P<platform>\S+)", re.MULTILINE)
    rx_version = re.compile(
        r"^(?:EXOS )?[Vv]ersion:\s+(?P<version>\S+)", re.MULTILINE)
    rx_active_slot = re.compile(r"^\*\S+\s[\d-]+\s(?P<slot_num>[\d-]).*$", re.MULTILINE)

    def execute(self):
        try:
            v = self.cli("debug hal show version")
        except self.CLISyntaxError:
            v = self.cli("debug hal show stacking active", ignore_errors=True)
            match = self.rx_active_slot.search(v)
            slot = match.group(1) if match else 1
            v = self.cli("debug hal show version slot %s" % slot)
        platform = self.rx_platform.search(v).group("platform")
        version = self.rx_version.search(v).group("version")
        return {
            "vendor": "Extreme",
            "platform": platform,
            "version": version
        }
