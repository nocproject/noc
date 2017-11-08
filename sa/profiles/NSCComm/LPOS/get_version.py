# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NSCComm.LPOS.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "NSCComm.LPOS.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^System ID\s+: (?P<platform>\S+)\s*\n"
        r"^Hardware version\s+: (?P<hardware>.+)\s*\n"
        r"^Software version\s+: LP ARM OS (?P<version>.+) \(.+\n"
        r"^Firmware version\s+: (?P<fw_version>\S+)\s*\n",
        re.MULTILINE
    )

    def execute(self):
        match = self.rx_ver.search(self.cli("stats", cached=True))
        return {
            "vendor": "NSCComm",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "HW version": match.group("hardware")
            }
        }
