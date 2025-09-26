# ---------------------------------------------------------------------
# DLink.DxS.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
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
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    # DES-1210-28/ME
    rx_result_des1210 = re.compile(
        r"(?P<count>\d+)\s+Packets Transmitted,\s+(?P<success>\d+)\s+Packets Received,\s+\d+%\s+Packets Loss",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def execute(
        self, address, count=None, source_address=None, size=None, df=None, *args, **kwargs
    ):
        cmd = "ping %s" % address
        if count:
            cmd += " times %d" % int(count)
        else:
            cmd += " times 5"
        if source_address:
            cmd += " source_ip %s" % source_address
        # Not implemented, may be in future firmware revisions ?
        # if size:
        #    cmd+=" size %d"%int(size)
        # if df:
        #    cmd+=" df-bit"
        r = self.cli(cmd)
        rx = self.find_re([self.rx_result, self.rx_result_des1210], r)
        match = rx.search(r)
        return {"success": int(match.group("success")), "count": int(match.group("count"))}
