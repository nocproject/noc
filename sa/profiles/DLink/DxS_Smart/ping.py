# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Smart.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.sa.profiles.DLink.DxS_Smart import DES1210
import re


<<<<<<< HEAD
class Script(BaseScript):
    name = "DLink.DxS_Smart.ping"
    interface = IPing
=======
class Script(NOCScript):
    name = "DLink.DxS_Smart.ping"
    implements = [IPing]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_result = re.compile(
        r"^\s*(?P<count>\d+) Packets Transmitted, (?P<success>\d+) "
        r"Packets Received, \d+% Packets Loss",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

<<<<<<< HEAD
    @BaseScript.match(DES1210)
=======
    @NOCScript.match(DES1210)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute_ping(self, address):
        cmd = "ping %s" % address
        match = self.rx_result.search(self.cli(cmd))
        if not match:
            raise self.NotSupportedError()
        return {
            "success": match.group("success"),
            "count": match.group("count"),
        }

<<<<<<< HEAD
    @BaseScript.match()
=======
    @NOCScript.match()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute_ping_other(self, address):
        raise self.NotSupportedError()
