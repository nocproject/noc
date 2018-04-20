# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS.ping
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
    name = "DLink.DxS.ping"
    interface = IPing
    rx_result = re.compile(
        r"^\s*Packets: Sent =\s*(?P<count>\d+), Received =\s*(?P<success>\d+), Lost =\s*\d+",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    # DES-1210-28/ME
    rx_result_des1210 = re.compile(
        r"(?P<count>\d+)\s+Packets Transmitted,\s+(?P<success>\d+)\s+Packets Received,\s+\d+%\s+Packets Loss",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    def execute(self, address, count=None, source_address=None,
                size=None, df=None, *args, **kwargs):
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
    name = "DLink.DxS.ping"
    implements = [IPing]
    rx_result = re.compile(r"^\s*Packets: Sent =\s*(?P<count>\d+), Received =\s*(?P<success>\d+), Lost =\s*\d+", re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self, address, count=None, source_address=None, size=None,
    df=None):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        cmd = "ping %s" % address
        if count:
            cmd += " times %d" % int(count)
        else:
            cmd += " times 5"
        if source_address:
            cmd += " source_ip %s" % source_address
<<<<<<< HEAD
        # Not implemented, may be in future firmware revisions ?
=======
        # Don't implemented, may be in future firmware revisions ?
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        #if size:
        #    cmd+=" size %d"%int(size)
        #if df:
        #    cmd+=" df-bit"
<<<<<<< HEAD
        r = self.cli(cmd)
        rx = self.find_re([self.rx_result, self.rx_result_des1210], r)
        match = rx.search(r)
=======
        match = self.rx_result.search(self.cli(cmd))
        if not match:
            raise self.NotSupportedError()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        r = {
            "success": int(match.group("success")),
            "count": int(match.group("count")),
        }
        return r
