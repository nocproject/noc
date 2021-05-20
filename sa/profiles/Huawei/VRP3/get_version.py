# ---------------------------------------------------------------------
# Huawei.VRP3.get_version
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Huawei.VRP3.get_version"
    interface = IGetVersion

    cache = True
    rx_ver = re.compile(r"\S+\s+(?P<version>\S+)\((?P<platform>\S+)\) Version , RELEASE SOFTWARE")
    rx_5103_old = re.compile(r"\s+MA5100(?P<version>\S+)\sRELEASE SOFTWARE")
    rx_bios = re.compile(r"\s+BIOS Version is\s+(?P<bios>\S+)")

    def execute(self):
        v = self.cli("show version")
        try:
            match = self.re_search(self.rx_ver, v)
            platform = match.group("platform")
            version = match.group("version")
        except self.UnexpectedResultError:
            match = self.rx_5103_old.search(v)
            version = match.group("version")
            platform = "MA5103"
        r = {
            "vendor": "Huawei",
            "platform": platform,
            "version": version,
        }
        bios = self.rx_bios.search(v)
        if bios:
            r.update({"attributes": {}})
            r["attributes"].update({"Boot PROM": bios.group("bios")})
        return r
