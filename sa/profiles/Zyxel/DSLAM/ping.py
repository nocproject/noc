# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.DSLAM.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Zyxel.DSLAM.ping"
    interface = IPing
    rx_result = re.compile(
        r"^\s*(ip: ping - )?reply (received )?from", re.MULTILINE)

    def execute(self, address, count=None, source_address=None, size=None,
                df=None):
        cmd = "ip ping %s" % address
        if count:
            cmd += " %d" % int(count)
        else:
            count = 3
        match = self.rx_result.search(self.cli(cmd))
        if match:
            success = count
        else:
            success = 0
        return {
            "success": int(success),
            "count": int(count)
        }
