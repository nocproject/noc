# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.MSAN.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "Zyxel.MSAN.DxS.ping"
    interface = IPing
    rx_result = re.compile(r"^\s*request timed out", re.MULTILINE)

    def execute(self, address, count=None, source_address=None, size=None,
    df=None):
        cmd = "ip ping %s" % address
        if count:
            cmd += " %d" % int(count)
        else:
            count = 3
        match = self.rx_result.search(self.cli(cmd))
        if match:
            success = 0
        else:
            success = count
        return {
            "success": int(success),
            "count": int(count)
        }
