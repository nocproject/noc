# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Taros.EAU.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "IRE-Polus.Taros.get_version"
    cache = True
    interface = IGetVersion

    def execute_snmp(self, **kwargs):
        try:
            sysObjID = self.snmp.get("1.3.6.1.2.1.1.2.0")  # sysObjectID
            if sysObjID == "1.3.6.1.4.1.14546.1.1.10":
                platform = self.snmp.get("1.3.6.1.4.1.14546.4.5.1.4.1.4.0")
                version = self.snmp.get("1.3.6.1.4.1.14546.4.5.1.4.1.2.0")
                serial = self.snmp.get("1.3.6.1.4.1.14546.4.5.1.4.1.3.0")
                hw_ver = self.snmp.get("1.3.6.1.4.1.14546.4.5.1.4.1.1.0")
            elif sysObjID == "1.3.6.1.4.1.35702.3.5":
                platform = self.snmp.get("1.3.6.1.4.1.35702.3.5.1.1.0")
                version = self.snmp.get("1.3.6.1.4.1.35702.3.5.1.4.0")
                serial = self.snmp.get("1.3.6.1.4.1.35702.3.5.1.2.0")
                hw_ver = self.snmp.get("1.3.6.1.4.1.35702.3.5.1.3.0")
            else:
                raise self.NotSupportedError
            return {
                "vendor": "IRE-Polus",
                "platform": platform,
                "version": version,
                "attributes": {"Serial Number": serial, "HW version": hw_ver},
            }
        except self.snmp.TimeOutError:
            raise self.NotSupportedError
