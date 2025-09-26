# ---------------------------------------------------------------------
# Qtech.BFC_PBIC_S.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Qtech.BFC_PBIC_S.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False

    def execute_snmp(self):
        o = self.snmp.get("1.3.6.1.2.1.1.1.0")
        o = o.split()
        platform = o[0]
        if len(o) == 3:
            version = "%s%s" % (o[1], o[2])
        else:
            version = "None"
        vendor = "Qtech"
        if "KUB" in platform:
            vendor = "Ttronics"
        return {"vendor": vendor, "version": version, "platform": platform}
