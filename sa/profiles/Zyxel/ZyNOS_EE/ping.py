# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS_EE.ping
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
    name = "Zyxel.ZyNOS_EE.ping"
    implements = [IPing]
    rx_result = re.compile(
        r"^\s+(?P<count>\d+)\s+(?P<success>\d+)\s+\d+\s+\d+\s+(?P<avg>\d+)\s+\d+\s+(?P<max>\d+)\s+(?P<min>\d+)",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None,
                size=None, df=None):
        cmd = "ip ping %s" % address
        success = 0
        count = 3  # 3 times by default
        min = 0
        avg = 0
        max = 0
        for match in self.rx_result.finditer(self.cli(cmd)):
            success = match.group("success")
            count = match.group("count")
            min = match.group("min")
            avg = match.group("avg")
            max = match.group("max")
        return {
            "success": success,
            "count": count,
            "min": min,
            "avg": avg,
            "max": max,
            }
