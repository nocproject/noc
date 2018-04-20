# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.ProCurve9xxx.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
=======
##----------------------------------------------------------------------
## HP.ProCurve9xxx.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re

rx_line = re.compile(r"^\d+\s+(?P<ip>\S+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+\d+\s+(?P<interface>\S+)")


<<<<<<< HEAD
class Script(BaseScript):
    name = "HP.ProCurve9xxx.get_arp"
    interface = IGetARP
=======
class Script(noc.sa.script.Script):
    name = "HP.ProCurve9xxx.get_arp"
    implements = [IGetARP]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        s = self.cli("show arp")
        r = []
        for l in s.split("\n"):
            match = rx_line.match(l.strip())
            if not match:
                continue
            type = match.group("type")
            mac = match.group("mac")
            if mac.lower() in ("incomplete" or "none") or \
            type.lower() in ("pending", "invalid"):
                continue
            else:
                r.append({
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("interface")
                })
        return r
