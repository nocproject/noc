# ---------------------------------------------------------------------
# MikroTik.RouterOS.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "MikroTik.RouterOS.ping"
    interface = IPing

    rx_result = re.compile(
        r"^\s*sent=(?P<sent>\d+) received=(?P<received>\d+) "
        r"packet-loss=\d+% min-rtt=(?P<min>\d+)ms "
        r"avg-rtt=(?P<avg>\d+)ms max-rtt=(?P<max>\d+)ms",
        re.MULTILINE,
    )
    rx_result1 = re.compile(
        r"^\s*sent=(?P<sent>\d+) received=(?P<received>\d+) packet-loss=\d+%", re.MULTILINE
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "/ping %s" % address
        if count:
            cmd += " count=%d" % int(count)
        else:
            cmd += " count=5"
        if source_address:
            cmd += " src-address=%s" % source_address
        if size:
            cmd += " size=%d" % int(size)
        if df:
            cmd += " do-not-fragment"
        c = self.cli(cmd)
        match = self.rx_result.search(c)
        if match:
            return {
                "success": match.group("received"),
                "count": match.group("sent"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            }
        match = self.rx_result1.search(c)
        return {"success": match.group("received"), "count": match.group("sent")}
