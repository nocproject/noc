# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Nateks.FlexGainACE16.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "Nateks.FlexGainACE16.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("show sysinfo", cached=True)
        pkv = parse_kv(
            {"1.hardware version": "hw", "2.software version": "sw", "3.serial number": "serial"}, v
        )

        return {
            "vendor": "Nateks",
            "platform": "ACE",
            "version": pkv["sw"],
            "attributes": {"HW version": pkv["hw"], "Serial Number": pkv["serial"]},
        }
