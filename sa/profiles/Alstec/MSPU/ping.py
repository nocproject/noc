# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Alstec.MSPU.ping"
    interface = IPing

    rx_line = re.compile(
        r"(?P<count>\d+) packets transmitted, (?P<success>\d+) received,")

    def execute(self, address, count=None, source_address=None,
                size=None, df=None, vrf=None):
        cmd = "ping %s" % address
        if count is not None:
            cmd += " count %d" % int(count)
        else:
            cmd += " count 5"
        if size is not None:
            cmd += " size %d" % int(size)
        match = self.rx_line.search(self.cli(cmd))
        return match.groupdict()
