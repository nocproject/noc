# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_license
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


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
        r"(^\s*nlevel: (?P<nlevel>\d+)\s*\n)?"
        r"(^\s*level: (?P<level>\S+)\s*\n)?"
        r"(^\s*features:.*(?P<features>\.*)$)?",
        re.MULTILINE | re.DOTALL,
    )

    def execute_cli(self):
        v = self.cli("system license print")
        match = self.re_search(self.rx_lic, v)
        if match.group("nlevel"):
            level = int(match.group("nlevel"))
        if match.group("level"):
            level = {"free": 1, "p1": 2, "p2": 3, "p-unlimited": 4}[match.group("level").lower()]
        r = {
            "software-id": match.group("sid"),
            "upgradable-to": match.group("upto"),
            "nlevel": level,
        }
        if match.group("features"):
            features = match.group("features").strip()
            r.update({"features": features})
        return r
