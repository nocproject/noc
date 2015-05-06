# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing
from noc.sa.profiles.DLink.DxS_Smart import DES1210
import re


class Script(NOCScript):
    name = "DLink.DxS_Smart.ping"
    implements = [IPing]
    rx_result = re.compile(
        r"^\s*(?P<count>\d+) Packets Transmitted, (?P<success>\d+) "
        r"Packets Received, \d+% Packets Loss",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    @NOCScript.match(DES1210)
    def execute_ping(self, address):
        cmd = "ping %s" % address
        match = self.rx_result.search(self.cli(cmd))
        if not match:
            raise self.NotSupportedError()
        return {
            "success": match.group("success"),
            "count": match.group("count"),
        }

    @NOCScript.match()
    def execute_ping_other(self, address):
        raise self.NotSupportedError()
