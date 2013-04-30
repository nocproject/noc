# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP


class Script(NOCScript):
    name = "f5.BIGIP.get_arp"
    implements = [IGetARP]

    # 10.10.10.10  10.10.10.10  0:50:56:99:77:6    /Common/VM_Net          29             resolved
    rx_line = re.compile(
        r"^(?P<name>\S+)\s+"
        r"(?P<address>\S+)\s+"
        r"(?P<mac>\S+)\s+"
        r"(?P<vlan>\S+)\s+"
        r"(?P<expire>\d+)\s+"
        r"resolved$",
        re.MULTILINE
    )

    def execute(self):
        r = []
        v = self.cli("show /net arp all")
        for match in self.rx_line.finditer(v):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
