# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.7200.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Alstec.7200.ping"
    interface = IPing

    rx_line = re.compile(
        r"(?P<count>\d+) packets transmitted, "
        r"(?P<success>\d+) packets received, "
        r"\d+% packet loss\n"
        r"round-trip \(msec\) min/avg/max = "
        r"(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None,
                size=None, df=None, vrf=None):
        cmd = "ping %s" % address
        if count:
            cmd += " count %d" % int(count)
        else:
            cmd += " count 5"
        match = self.rx_line.search(self.cli(cmd))
        return match.groupdict()
