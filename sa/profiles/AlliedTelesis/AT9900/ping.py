# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT9900.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing


class Script(NOCScript):
    name = "AlliedTelesis.AT9900.ping"
    implements = [IPing]
    rx_result = re.compile("Echo reply (?P<count>\d+) from [\d\.]+ time delay (?P<resp>\d+.\d+) ms", re.MULTILINE | re.DOTALL)

    def execute(self, address, size=None, count=None, timeout=None):
        cmd = "ping %s" % address
        pr = self.cli(cmd).replace("\n\n", "\n")
        r = []
        n = 0
        avg1 = 0
        for l in pr.split('\n'):
            match = self.rx_result.match(l.strip())
            if match:
                r += [match.group("resp")]
                n += float(match.group("resp"))
                count = match.group("count")
        avg1 = round(float(n / len(r)), 3)
        return {
            "success": len(r),
            "count": count,
            "min": min(r),
            "avg": avg1,
            "max": max(r)
        }
