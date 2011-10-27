# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetARP

rx_line = re.compile(r"^vlan+\s+\d+\s+(?P<interface>\S+)+\s+(?P<ip>\S+)+\s+(?P<mac>\S+)+\s+\S", re.MULTILINE)

class Script(noc.sa.script.Script):
    name = "Eltex.MES.get_arp"
    implements=[IGetARP]

    def execute(self):
        r = []

# BUG http://bt.nocproject.org/browse/NOC-36
        # Try snmp first
#        if self.snmp and self.access_profile.snmp_ro:
#            try:
#                for s in self.snmp.get_table("1.3.6.1.2.1.4.22"): # 
#                    print s
#                    r.append( {"ip":match.group("ip"), "mac":match.group("mac"), "interface":match.group("interface")} )
#                return r
#            except self.snmp.TimeOutError:
#                pass

        # Fallback to CLI
        for match in rx_line.finditer(self.cli("show arp")):
            mac = match.group("mac")
            if mac.lower() == "incomplete":
                r.append( {"ip":match.group("ip"), "mac":None, "interface":None} )
            else:
                r.append( {"ip":match.group("ip"), "mac":match.group("mac"), "interface":match.group("interface")} )
        return r
