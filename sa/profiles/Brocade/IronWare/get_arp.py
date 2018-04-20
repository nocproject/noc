# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Brocade.IronWare.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Brocade.IronWare.get_arp"
    interface = IGetARP
=======
##----------------------------------------------------------------------
## Brocade.IronWare.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP


class Script(NOCScript):
    name = "Brocade.IronWare.get_arp"
    implements = [IGetARP]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(r"^\d+\s+(?P<ip>\S+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+\d+\s+(?P<interface>\S+)")

    def execute(self):
        s = self.cli("show arp")
        r = []
        for l in s.splitlines():
            match = rx_line.match(l.strip())
            if not match:
                continue
            type = match.group("type")
            mac = match.group("mac")
            if (mac.lower() in ("incomplete" or "none") or
                type.lower() in ("pending", "invalid")):
                continue
            else:
                r += [{
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("interface")
                }]
        return r
