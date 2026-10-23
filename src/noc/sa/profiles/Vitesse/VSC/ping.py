# ---------------------------------------------------------------------
# Vitesse.VSC.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
from noc.core.validators import is_ipv4, is_ipv6
import re


class Script(BaseScript):
    name = "Vitesse.VSC.ping"
    interface = IPing
    rx_result = re.compile(r"Sent (?P<count>\d+) packets, received (?P<success>\d+) OK, \d+ bad")

    def execute(self, address, count=None, source_address=None, size=None, df=None, vrf=None):
        if is_ipv4(address):
            cmd = f"ping ip {address}"
        elif is_ipv6(address):
            cmd = f"ping ipv6 {address}"
        if count:
            cmd += f" repeat {int(count)}"
        if size:
            cmd += f" size {int(size)}"
        s = self.cli(cmd)
        match = self.rx_result.search(s)
        return match.groupdict()
