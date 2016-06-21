# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Zyxel.ZyNOS.ping"
    interface = IPing
    rx_result = re.compile(r"^\s+(?P<count>\d+)\s+(?P<success>\d+)\s+\d+\s+" \
                            "\d+\s+(?P<avg>\d+)\s+\d+\s+(?P<max>\d+)\s+" \
                            "(?P<min>\d+)", re.MULTILINE)

    def execute(self, address, size=None, *args, **kwargs):
        cmd = "ping %s" % address
        if size:
            cmd += " size %d" % size
        # some default values
        cnt = 6
        success = 0
        avg = 0
        max = 0
        min = 1000
        for match in self.rx_result.finditer(self.cli(cmd)):
            success += int(match.group("success"))
            if int(match.group("min")) < min:
                min = int(match.group("min"))
            if int(match.group("max")) > max:
                max = int(match.group("max"))
            avg += int(match.group("avg"))
        return {
            "success": success,
            "count": cnt,
            "min": min if success > 0 else 0,
            "avg": avg / success if success > 0 else 0,
            "max": max,
        }
