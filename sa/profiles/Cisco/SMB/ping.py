# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Cisco.SMB.ping
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Cisco.SMB.ping"
    interface = IPing
=======
##----------------------------------------------------------------------
## Cisco.SMB.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing


class Script(NOCScript):
    name = "Cisco.SMB.ping"
    implements = [IPing]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_result = re.compile(r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) packets received.*round-trip \(ms\) min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)", re.MULTILINE | re.DOTALL)

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "ping ip %s" % address
        if count:
            cmd += " count %d" % int(count)
        if source_address:
            cmd += " source %s" % source_address
        if size:
            cmd += " size %d" % int(size)
        if df:
            # no such option in CLI:
            raise self.NotSupportedError()
            cmd += " df-bit"
        pr = self.cli(cmd)
        match = self.rx_result.search(pr)
        return {
<<<<<<< HEAD
            "success": match.group("success"),
            "count": match.group("count"),
            "min": match.group("min"),
            "avg": match.group("avg"),
            "max": match.group("max"),
        }
=======
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            }
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
