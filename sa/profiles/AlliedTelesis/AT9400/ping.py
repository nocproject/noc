# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT9400.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "AlliedTelesis.AT9400.ping"
    interface = IPing
    rx_result = re.compile(r"^Reply from [\d\.]+ time=(?P<resp>\d+)ms$", re.MULTILINE | re.DOTALL)

    def execute(self, address, size=None, count=None, timeout=None):
        cmd = "ping %s" % address
        pr = self.cli(cmd)
        r = []
        n = 0
        for l in pr.split("\n"):
            match = self.rx_result.match(l.strip())
            if match:
                r += [match.group("resp")]
                n += int(match.group("resp"))
        avg1 = int(n / len(r))
        return {
                "success": len(r),
                "count": 4,
                "min": min(r),
                "avg": avg1,
                "max": max(r)
               }
