# -*- coding: utf-8 -*- 
# ---------------------------------------------------------------------
# Ruckus.SmartZone.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "Ruckus.SmartZone.get_cpe"
    interface = IGetCPE

    type_map = {
        "Disconnect": "inactive",
        "Connect": "active",
    }

    def execute(self, mac=None):
        r = []
        if self.has_snmp():
            try:                            
                for v in self.snmp.getnext("1.3.6.1.4.1.25053.1.4.2.1.1.2.2.1.5", cached=True):
                    cpename = v[1]
                    cpeid = v[0][len("1.3.6.1.4.1.25053.1.2.2.4.1.1.1.1.5") + 1:]
                    s = str(self.snmp.get("1.3.6.1.4.1.25053.1.4.2.1.1.2.2.1.1.%s" % cpeid, cached=True))
                    mac = MACAddressParameter().clean(s) # convert mac
                    #print "%s\n" % mac                                             
                    key = ".".join(str(int(x, 16)) for x in mac.split(":"))  # convert mac - > bytes
                    # print "%s\n" % key
                    status = self.snmp.get("1.3.6.1.4.1.25053.1.4.2.1.1.2.2.1.16.6.%s" % key, cached=True)
                    ip = self.snmp.get("1.3.6.1.4.1.25053.1.4.2.1.1.2.2.1.10.%s" % cpeid, cached=True)
                    location = self.snmp.get("1.3.6.1.4.1.25053.1.4.2.1.1.2.2.1.19.6.%s" % cpeid, cached=True)
                    description = self.snmp.get("1.3.6.1.4.1.25053.1.4.2.1.1.2.2.1.22.6.%s" % key, cached=True)
                    sn = self.snmp.get("1.3.6.1.4.1.25053.1.4.2.1.1.2.2.1.9.6.%s" % key, cached=True)
                    model = self.snmp.get("1.3.6.1.4.1.25053.1.4.2.1.1.2.2.1.8.6.%s" % key, cached=True)
                    version = self.snmp.get("1.3.6.1.4.1.25053.1.4.2.1.1.2.2.1.7.6.%s" % key, cached=True)
                    r.append({
                        "vendor": "Ruckus",
                        "model": model,
                        "version": version,
                        "mac": mac,
                        "status": self.type_map[str(status)],
                        "id": cpeid,
                        "global_id": mac,
                        "type": "ap",
                        "name": cpename,
                        "ip": ip,
                        "serial": sn,
                        "description": description,
                        "location": location
                        })
                    #print ("%s\n" % r)
                return r
            except self.snmp.TimeOutError:
                pass
