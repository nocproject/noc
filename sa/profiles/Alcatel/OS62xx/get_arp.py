# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.OS62xx.get_arp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
=======
##----------------------------------------------------------------------
## Alcatel.OS62xx.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re

rx_line = re.compile(
    r"^\s*(?P<interface>\d\S+)\s+(?P<ip>\d\S+)\s+(?P<mac>\S+)\s+(?:Dynamic|Static)", re.MULTILINE)


<<<<<<< HEAD
class Script(BaseScript):
    name = "Alcatel.OS62xx.get_arp"
    interface = IGetARP
=======
class Script(NOCScript):
    name = "Alcatel.OS62xx.get_arp"
    implements = [IGetARP]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        r = []
        for match in rx_line.finditer(self.cli("show arp")):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
