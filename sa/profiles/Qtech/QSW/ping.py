# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Qtech.QSW.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Qtech.QSW.ping"
    interface = IPing
=======
##----------------------------------------------------------------------
## Qtech.QSW.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IPing


class Script(noc.sa.script.Script):
    name = "Qtech.QSW.ping"
    implements = [IPing]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) (packets received|received), \d+% packet loss$",
        re.MULTILINE)
    rx_stat = re.compile(
        r"^round-trip \(ms\)\s+min/avg/max = (?P<min>.+)/(?P<avg>.+)/(?P<max>.+)$",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None,
        size=None, df=None):
        cmd = "ping"
        if count:
            cmd += " -c %d" % int(count)
        if size:
            cmd += " -s %d" % int(size)

        """
        # Don't implemented, may be in future firmware revisions ?
        if source_address:
            cmd+=" source %s" % source_address
        if df:
            cmd+=" df-bit"
        """

        cmd += " %s" % address
        ping = self.cli(cmd)
        result = self.rx_result.search(ping)
        r = {
            "success": result.group("success"),
            "count": result.group("count"),
            }
        stat = self.rx_stat.search(ping)
        if stat:
            r.update({
                    "min": stat.group("min"),
                    "avg": stat.group("avg"),
                    "max": stat.group("max"),
                    })
        return r
