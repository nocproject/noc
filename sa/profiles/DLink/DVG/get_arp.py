# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DVG.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "DLink.DVG.get_arp"
    interface = IGetARP
    cache = True

    def execute(self):
        r = []
        # BUG http://bt.nocproject.org/browse/NOC-36
        # Only one way: SNMP.
        if self.has_snmp():
            try:
                for i, ip, mac, i in self.snmp.join([
                    "1.3.6.1.2.1.4.22.1.3",
                    "1.3.6.1.2.1.4.22.1.2",
                    "1.3.6.1.2.1.4.22.1.1"
                ]):  # IP-MIB
                    r += [{"ip": ip, "mac": mac, "interface": self.snmp.get(
                        "1.3.6.1.2.1.2.2.1.2" + '.' + i, cached=True)}]  # IF-MIB
                return r
            except self.snmp.TimeOutError:
                raise self.NotSupportedError()
