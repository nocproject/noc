# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NAG.SNR.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "NAG.SNR.get_arp"
    interface = IGetARP
    cache = True

    def execute(self):
        r = []
        # Try SNMP first
        if self.has_snmp():
            try:
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.4.22.1.1", "1.3.6.1.2.1.4.22.1.2",
                    "1.3.6.1.2.1.4.22.1.3"], bulk=True):
                    iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." + v[1],
                        cached=True)  # IF-MIB
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
