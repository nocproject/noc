# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.ping"
    interface = IPing
=======
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing
import re


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.ping"
    implements = [IPing]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_result = re.compile(
        r"^Success rate is \d+ percent \((?P<success>\d+)/(?P<count>\d+)\)"
        r"(, round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)"
        r" ms)?", re.MULTILINE | re.DOTALL)

    def execute(self, address, count=None, source_address=None, size=None, \
        df=None):
        if ":" in address:
            cmd = "ping ipv6 %s" % address
            if count:
                cmd += " -n %d" % int(count)
            if source_address:
                cmd += " -s %s" % source_address
            if size:
                cmd += " -l %d" % int(size)
        else:
            cmd = "ping ip %s" % address
            if count:
                cmd += " ntimes %d" % int(count)
            if source_address:
                cmd += " source %s" % source_address
            if size:
                cmd += " length %d" % int(size)
        # Don't implemented, may be in future firmware revisions ?
        #if df:
        #    cmd+=" df-bit"
        match = self.rx_result.search(self.cli(cmd))
        if not match:
            raise self.NotSupportedError()
        return {
                "success": int(match.group("success")),
                "count": int(match.group("count")),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max")
            }
