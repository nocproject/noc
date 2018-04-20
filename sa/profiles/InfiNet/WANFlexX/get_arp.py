# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_arp"
    interface = IGetARP
    rx_arp = re.compile(r"^(?P<ip>\S+)\s+at\s+(?P<mac>[0-9a-fA-F]+)\s+via\s+"
                        r"(?P<interface>\S+)$",
                        re.MULTILINE)

    def execute(self):
        arp = self.cli("arp view")
        res = []
        for match in self.rx_arp.finditer(arp):
            res += [{
=======
##----------------------------------------------------------------------
## InfiNet.WANFlexX.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.interfaces import IGetARP
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "InfiNet.WANFlexX.get_arp"
    implements = [IGetARP]
    rx_arp = re.compile(r"^(?P<ip>\S+)\s+at\s+(?P<mac>[0-9a-f]+)\s+via\s+"
                        r"(?P<interface>\S+)$", re.MULTILINE)

    def execute(self):
        arp = self.cli("arp view")
        r = []
        for match in self.rx_arp.finditer(arp):
            r += [{
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
<<<<<<< HEAD
        return res
=======
        return r
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
