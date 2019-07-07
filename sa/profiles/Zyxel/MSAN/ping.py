# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.MSAN.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "Zyxel.MSAN.ping"
    interface = IPing

    rx_result = re.compile(r"^\s*(ip: ping - )?reply (received )?from", re.MULTILINE)
    rx_result1 = re.compile(r"^\s*(?P<sent>\d+)\s+(?P<recv>\d+)\s+\d+\s+\d+\s+\d+", re.MULTILINE)

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "ip ping %s" % address
        if count:
            cmd += " %d" % int(count)
        else:
            count = 3
        c = self.cli(cmd)
        match = self.rx_result.search(c)
        if match:
            success = count
        else:
            match = self.rx_result1.findall(c)
            if match:
                success = match[-1][1]
            else:
                success = 0
        return {"success": int(success), "count": int(count)}
