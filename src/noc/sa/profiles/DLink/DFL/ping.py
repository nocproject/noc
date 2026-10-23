# ---------------------------------------------------------------------
# DLink.DxS.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "DLink.DFL.ping"
    interface = IPing
    rx_result = re.compile(
        r"^\s*Ping Results:\s*Sent:\s*(?P<count>\d+),\s*Received:\s*(?P<succes>\d+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = f"ping {address}"
        if count:
            cmd += f" -count={int(count)}"
        else:
            cmd += " -count=5"
        if source_address:
            cmd += f" -srcip={source_address}"
        if size:
            cmd += f" -length={size}"

        result = self.cli(cmd)
        match = self.rx_result.search(result)
        return match.groupdict()
