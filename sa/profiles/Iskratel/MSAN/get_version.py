# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MSAN.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Iskratel.MSAN.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(r"Software Version\.+ (?P<version>\S+)")

    def execute_cli(self):
        v = self.profile.get_hardware(self)
        if "api_ver" in v and v["api_ver"] is not None:
            version = v["api_ver"]
        else:
            c = self.cli("show version")
            match = self.rx_ver.search(c)
            version = match.group("version")
        return {
            "vendor": "Iskratel",
            "platform": v["platform"],
            "version": version,
            "attributes": {"Serial Number": v["serial"]},
        }
