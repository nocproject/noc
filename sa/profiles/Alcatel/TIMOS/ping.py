# ----------------------------------------------------------------------
# Alcatel.TIMOS.ping
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Alcatel.TIMOS.ping"
    interface = IPing

    rx_result = re.compile(
        r"(?P<count>\d+)\s+packets transmitted,\s+(?P<success>\d+)\s+packets received,\s+\d+\.\d+%\s+packet loss\s*\n"
        r"round-trip min = (?P<min>\d+\.\d+)ms, avg = (?P<avg>\d+\.\d+)ms, max = (?P<max>\d+\.\d+)ms, stddev = \d+\.\d+ms",
        re.MULTILINE,
    )
    rx_result1 = re.compile(
        r"(?P<count>\d+)\s+packets transmitted,\s+(?P<success>0)\s+packets received,\s+\d+%\s+packet loss",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def execute(
        self, address, count=None, source_address=None, size=None, df=None, *args, **kwargs
    ):
        cmd = "ping %s" % address
        if count:
            cmd += " times %d" % int(count)
        else:
            count = 5
        if source_address:
            cmd += " source %s" % source_address
        if size:
            cmd += " size %d" % int(size)
        if df:
            cmd += " do-not-fragment"
        v = self.cli(cmd)
        match = self.rx_result.search(v)
        if match:
            return match.groupdict()
        match = self.rx_result1.search(v)
        if match:
            return match.groupdict()
        raise self.NotSupportedError()
