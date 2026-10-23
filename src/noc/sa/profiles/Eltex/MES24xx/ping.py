# ---------------------------------------------------------------------
# Eltex.MES24xx.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
from noc.core.validators import is_ipv4, is_ipv6


class Script(BaseScript):
    name = "Eltex.MES24xx.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) Packets Transmitted, (?P<success>\d+) Packets Received, \d+% Packets Loss",
        re.MULTILINE,
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        if is_ipv4(address):
            cmd = f"ping ip {address}"
        elif is_ipv6(address):
            cmd = f"ping ipv6 {address}"
        if count:
            cmd += f" count {int(count)}"
        if size:
            cmd += f" size {int(size)}"
        if source_address:
            cmd += f" source {source_address}"
        if df:
            cmd += " df-bit"
        ping = self.cli(cmd)
        match = self.rx_result.search(ping)
        return {"success": match.group("success"), "count": match.group("count")}
