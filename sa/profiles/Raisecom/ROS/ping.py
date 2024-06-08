# ---------------------------------------------------------------------
# Raisecom.ROS.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Raisecom.ROS.ping"
    interface = IPing
    rx_result = re.compile(
        r"^(?P<success>\d+)\s+packets transmitted,\s+"
        r"(?P<count>\d+)\s+packets received,.+"
        r"min/avg/max\s+=\s+(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)?",
        re.MULTILINE | re.DOTALL,
    )

    def execute_cli(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "ping %s" % address
        if self.is_iscom2624g:
            if count:
                cmd += " c %d" % int(count)
            else:
                cmd += " c 5"
            if size:
                cmd += " s %d" % int(size)
        else:
            if count:
                cmd += " count %d" % int(count)
            else:
                cmd += " count 5"
            if size:
                cmd += " size %d" % int(size)
        pr = self.cli(cmd)
        if " is alive" in pr:
            return {"success": 1, "count": 1, "min": 0, "avg": 0, "max": 0}
        elif "no answer from" in pr:
            return {"success": 0, "count": 1}
        match = self.rx_result.search(pr)
        return {
            "success": match.group("success"),
            "count": match.group("count"),
            "min": match.group("min"),
            "avg": match.group("avg"),
            "max": match.group("max"),
        }
