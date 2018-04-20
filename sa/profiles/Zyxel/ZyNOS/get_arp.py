# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Zyxel.ZyNOS.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

# Python modules
import re
# NOC modules
<<<<<<< HEAD
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_arp"
    interface = IGetARP
=======
from noc.sa.interfaces import IGetARP
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_arp"
    implements = [IGetARP]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_arp = re.compile(r"^\s+\d+\s+(?P<ip>\S+)\s+(?P<mac>\S+)\s+"
                        r"(?P<interface>\d+).*$",
                        re.MULTILINE)

    def execute(self):
        arp = self.cli("show ip arp")
        r = []
        for match in self.rx_arp.finditer(arp):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
