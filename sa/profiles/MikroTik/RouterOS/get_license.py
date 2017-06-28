# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_license
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modiles
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlicense import IGetLicense


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_license"
    cache = True
    interface = IGetLicense
    rx_lic = re.compile(
        r"^\s*(?:software|system)-id: (?P<q>\"?)(?P<sid>\S+?)(?P=q)\n"
        r"(^\s*upgradable-to: (?P<upto>\S+)\n)?"
        r"(^\s*nlevel: (?P<nlevel>\d+)\n)?"
        r"(^\s*level: (?P<level>\S+)\n)?"
        r"(^\s*features:.*(?P<features>\.*)$)?",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("system license print")
        match = self.re_search(self.rx_lic, v)
        if match.group("nlevel"):
            level = int(match.group("nlevel"))
        if match.group("level"):
            level = {
                "free": 1, "p1": 2, "p2": 3, "p-unlimited": 4
            }[match.group("level").lower()]
        r = {
            "software-id": match.group("sid"),
            "upgradable-to": match.group("upto"),
            "nlevel": level,
        }
        features = match.group("features").strip()
        if features:
            r.update({"features": features})
        return r
