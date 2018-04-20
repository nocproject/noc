# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DVG.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "DLink.DVG.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) "
        r"(packets received|received), \d+% packet loss$",
=======
##----------------------------------------------------------------------
## DLink.DVG.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IPing


class Script(noc.sa.script.Script):
    name = "DLink.DVG.ping"
    implements = [IPing]

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) (packets received|received), \d+% packet loss$",
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        re.MULTILINE)
    rx_stat = re.compile(
        r"^round-trip min/avg/max = (?P<min>.+)/(?P<avg>.+)/(?P<max>.+) ms$",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None, size=None,
                df=None):
        cmd = "ping %s" % address
        if count:
            cmd += " %d" % int(count)
        else:
            cmd += " 5"
        if size:
            cmd += " %d" % int(size)
        else:
            cmd += " 64"
        ping = self.cli(cmd)
        result = self.rx_result.search(ping)
        if result:
            r = {
                "success": result.group("success"),
<<<<<<< HEAD
                "count": result.group("count")
=======
                "count": result.group("count"),
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                }
        else:
            raise self.NotSupportedError()
        stat = self.rx_stat.search(ping)
        if stat:
            r.update({
                "min": stat.group("min"),
                "avg": stat.group("avg"),
<<<<<<< HEAD
                "max": stat.group("max")
=======
                "max": stat.group("max"),
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                })
        return r
