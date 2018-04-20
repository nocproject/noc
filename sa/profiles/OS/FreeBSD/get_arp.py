# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# OS.FreeBSD.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "OS.FreeBSD.get_arp"
    interface = IGetARP
=======
##----------------------------------------------------------------------
## OS.FreeBSD.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
import re


class Script(NOCScript):
    name = "OS.FreeBSD.get_arp"
    implements = [IGetARP]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(
        r"^\S+\s+\((?P<ip>\S+)\)\s+\S+\s+(?P<mac>[0-9a-fA-F:]+)\s+\S+\s+"
        r"(?P<interface>\S+)", re.MULTILINE | re.DOTALL)

    def execute(self, vrf=None):
<<<<<<< HEAD
        s = self.cli("arp -an")
=======
        if vrf:
            s = self.cli("setfib %d arp -an" % vrf)
        else:
            s = self.cli("arp -an")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        r = []
        for match in self.rx_line.finditer(s):
            if match.group("mac") == "FF:FF:FF:FF:FF:FF":
                continue
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
