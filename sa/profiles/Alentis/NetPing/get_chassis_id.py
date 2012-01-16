# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alentis.NetPing.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "Alentis.NetPing.get_chassis_id"
    implements = [IGetChassisID]
    cache = True

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                mac = self.snmp.get("1.3.6.1.2.1.2.2.1.6.1", cached=True)
                return mac
            except self.snmp.TimeOutError:
                pass

        # Fallback to HTTP
        mac = self.http.get("/setup_get.cgi")
        mac = mac.split(",mac:'")[1]
        mac = mac.split("',ip:'")[0]
        return mac
