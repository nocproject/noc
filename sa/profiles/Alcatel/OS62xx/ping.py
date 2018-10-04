# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alcatel.OS62xx.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "Alcatel.OS62xx.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+% packet loss\n", re.MULTILINE)
    rx_result1 = re.compile(
        "^round-trip \(ms\) min/avg/max = "
        r"(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)?", re.MULTILINE)

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
        r = {
            "success": match.group("success"),
            "count": match.group("count"),
        }
        match = self.rx_result1.search(pr)
        if match:
            r.update({
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max")
            })
        return r
