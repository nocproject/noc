# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlliedTelesis.AT8500.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8500.ping"
    interface = IPing
    rx_result = re.compile(
        r"^Reply from [\d\.]+ time=(?P<resp>\d+)ms$",
=======
##----------------------------------------------------------------------
## AlliedTelesis.AT8500.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing
import re


class Script(NOCScript):
    name = "AlliedTelesis.AT8500.ping"
    implements = [IPing]
    rx_result = re.compile(r"^Reply from [\d\.]+ time=(?P<resp>\d+)ms$",
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        re.MULTILINE | re.DOTALL)

    def execute(self, address, size=None, count=None, timeout=None):
        cmd = "ping %s" % address
        pr = self.cli(cmd)
        r = []
        n = 0
        for l in pr.split("\n"):
            match = rx_result.match(l.strip())
            if match:
                r.append(match.group("resp"))
                n += int(match.group("resp"))
        avg1 = int(n / len(r))
        return {
                "success": len(r),
                "count": 4,
                "min": min(r),
                "avg": avg1,
                "max": max(r)
               }
