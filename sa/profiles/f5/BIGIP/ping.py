# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing


class Script(NOCScript):
    name = "f5.BIGIP.ping"
    implements = [IPing]

    rx_result = re.compile(
        r"(?P<count>\d+) packets transmitted, "
        r"(?P<success>\d+) received, \S+% packet loss, "
        r"time \d+ms\nrtt min/avg/max/mdev = (?P<min>\S+)/(?P<avg>\S+)/(?P<max>\S+)/\S+ ms",
        re.MULTILINE | re.DOTALL)

    def execute(self, address, count=None, source_address=None, size=None,
    df=None):
        cmd = ["run /util ping"]
        cmd += ["-c %d" % (count if count else 5)]
        if size:
            cmd += ["-s %d" % size]
        cmd += [address]
        cmd = " ".join(cmd)
        pr = self.cli(cmd)
        match = self.re_search(self.rx_result, pr)
        return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max")
        }
