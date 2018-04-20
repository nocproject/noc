# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "DLink.DFL.ping"
    interface = IPing
=======
##----------------------------------------------------------------------
## DLink.DxS.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing
import re


class Script(NOCScript):
    name = "DLink.DFL.ping"
    implements = [IPing]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_result = re.compile(r"^\s*Ping Results:\s*Sent:\s*(?P<count>\d+),\s*Received:\s*(?P<succes>\d+)", re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self, address, count=None, source_address=None, size=None,
        df=None):
        cmd = "ping %s" % address
        if count:
            cmd += " -count=%d" % int(count)
        else:
            cmd += " -count=5"
        if source_address:
            cmd += " -srcip=%s" % source_address
        if size:
            cmd += " -length=%s" % size

        result = self.cli(cmd)
        match = self.rx_result.search(result)
        r = match.groupdict()
        return r
