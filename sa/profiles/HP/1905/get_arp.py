# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1905.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetARP


class Script(noc.sa.script.Script):
    name = "HP.1905.get_arp"
    implements = [IGetARP]
    cache = True

    def execute(self):
        r = []
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.4.22.1.1", "1.3.6.1.2.1.4.22.1.2",
                    "1.3.6.1.2.1.4.22.1.3"], bulk=True):
                    iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." + v[1],
                        cached=True)  # IF-MIB
                    if not iface:
                        oid = "1.3.6.1.2.1.2.2.1.2." + v[1]
                        iface = self.snmp.get(oid, cached=True)
                    mac = ":".join(["%02x" % ord(c) for c in v[2]])
                    ip = ["%02x" % ord(c) for c in v[3]]
                    ip = ".".join(str(int(c, 16)) for c in ip)
                    r.append({"ip": ip,
                            "mac": mac,
                            "interface": iface,
                            })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
