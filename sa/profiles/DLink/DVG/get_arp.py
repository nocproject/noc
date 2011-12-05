# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DVG.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetARP


class Script(noc.sa.script.Script):
    name = "DLink.DVG.get_arp"
    implements = [IGetARP]
    cache = True

    def execute(self):
        r = []
        # BUG http://bt.nocproject.org/browse/NOC-36
        # Only one way: SNMP.
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for ip, mac, i in self.snmp.join_tables("1.3.6.1.2.1.4.22.1.3",
                                                        "1.3.6.1.2.1.4.22.1.2",
                                                        "1.3.6.1.2.1.4.22.1.1",
                                                        bulk=True,
                                                        cached=True):  # IP-MIB
                    r += [{"ip": ip, "mac": mac, "interface": self.snmp.get(
                        "1.3.6.1.2.1.2.2.1.2" + '.' + i, cached=True)}]  # IF-MIB
                return r
            except self.snmp.TimeOutError:
                raise self.NotSupportedError()
