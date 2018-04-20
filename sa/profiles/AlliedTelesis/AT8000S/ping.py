# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000S.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8000S.ping"
    interface = IPing
    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+% packet loss\nround-trip \(ms\) min/avg/max = "
        r"(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)?", re.MULTILINE)
=======
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing
import re


class Script(NOCScript):
    name = "AlliedTelesis.AT8000S.ping"
    implements = [IPing]
    rx_result = re.compile(r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) packets received, \d+% packet loss\nround-trip \(ms\) min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)?", re.MULTILINE | re.DOTALL)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self, address, size=None, count=None, timeout=None):
        cmd = "ping %s" % address
        if size:
            cmd += " size %d" % int(size)
        if count:
            cmd += " count %d" % int(count)
        if timeout:
            cmd += " timeout %d" % int(timeout)
        pr = self.cli(cmd)
        pr = self.strip_first_lines(pr, 1)
        match = self.rx_result.search(pr)
        return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            }
