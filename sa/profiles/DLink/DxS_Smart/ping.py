# ---------------------------------------------------------------------
# DLink.DxS_Smart.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "DLink.DxS_Smart.ping"
    interface = IPing
    rx_result = re.compile(
        r"^\s*(?P<count>\d+) Packets Transmitted, (?P<success>\d+) "
        r"Packets Received, \d+% Packets Loss",
        re.MULTILINE | re.IGNORECASE,
    )

    def execute_cli(self, address):
        if self.is_has_cli:
            cmd = "ping %s" % address
            match = self.rx_result.search(self.cli(cmd))
            if not match:
                raise self.NotSupportedError()
            return {"success": match.group("success"), "count": match.group("count")}
        raise self.NotSupportedError()
