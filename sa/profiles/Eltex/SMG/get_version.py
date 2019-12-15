# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.SMG.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Eltex.SMG.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        if self.has_snmp():
            try:
                v = self.snmp.get("1.3.6.1.4.1.35265.1.29.3.0", cached=True)
                # v = None
                if v:
                    match = self.re_search(r"^V\.(?P<version>\S+)\s(?P<platform>\d+)", v)
                    version = match.group("version")
                    platform = "SMG-" + match.group("platform")
                    return {"vendor": "Eltex", "platform": platform, "version": version}
            except self.snmp.TimeOutError:
                pass
        self.cli("sh")
        version = self.cli("cat /usr/local/version")
        # platform = self.cli("cat /usr/share/mibs/eltex/eltex-smg.mib")
        return {"vendor": "Eltex", "platform": "SMG", "version": version}
