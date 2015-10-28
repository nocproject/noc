# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
from noc.sa.profiles.DLink.DxS_Smart import DES1210
import re


class Script(BaseScript):
    name = "DLink.DxS_Smart.ping"
    interface = IPing
    rx_result = re.compile(
        r"^\s*(?P<count>\d+) Packets Transmitted, (?P<success>\d+) "
        r"Packets Received, \d+% Packets Loss",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    @BaseScript.match(DES1210)
    def execute_ping(self, address):
        cmd = "ping %s" % address
        match = self.rx_result.search(self.cli(cmd))
        if not match:
            raise self.NotSupportedError()
        return {
            "success": match.group("success"),
            "count": match.group("count"),
        }

    @BaseScript.match()
    def execute_ping_other(self, address):
        raise self.NotSupportedError()
