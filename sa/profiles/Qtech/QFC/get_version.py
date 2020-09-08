# ---------------------------------------------------------------------
# Qtech.QFC.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Qtech.QFC.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False

    def execute_snmp(self):
        try:
            platform = self.snmp.get("1.3.6.1.4.1.27514.102.0.1")
            oid = 102
        except Exception:
            platform = self.snmp.get("1.3.6.1.4.1.27514.103.0.1")
            oid = 103
        version = self.snmp.get("1.3.6.1.4.1.27514.%s.0.2" % oid)
        sn = self.snmp.get("1.3.6.1.4.1.27514.%s.0.3" % oid)
        result = {
            "vendor": "Qtech",
            "version": version,
            "platform": platform,
            "attributes": {"Serial Number": sn},
        }
        return result
