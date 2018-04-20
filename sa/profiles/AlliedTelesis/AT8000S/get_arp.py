# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000S.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8000S.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^vlan \d+\s+(?P<interface>(?:\d/)?[ge]\d+)\s+(?P<ip>\S+)\s+"
        r"(?P<mac>[\d:a-f]+)\s+")
=======
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
import re


class Script(NOCScript):
    name = "AlliedTelesis.AT8000S.get_arp"
    implements = [IGetARP]
    rx_line = re.compile(r"^vlan \d+\s+(?P<interface>(?:\d/)?[ge]\d+)\s+(?P<ip>\S+)\s+(?P<mac>[\d:a-f]+)\s+")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        s = self.cli("show arp")
        r = []
        for l in s.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            r.append({
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
                })
        return r
