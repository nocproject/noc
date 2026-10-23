# ---------------------------------------------------------------------
# OS.FreeBSD.get_uptime
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_uptime import Script as BaseScript
from noc.sa.interfaces.igetuptime import IGetUptime


class Script(BaseScript):
    name = "OS.FreeBSD.get_uptime"
    interface = IGetUptime

    rx_uptime1 = re.compile(r"up (?P<s>\d+) secs, \d+ user")
    rx_uptime2 = re.compile(r"up (?P<m>\d+) mins, \d+ user")
    rx_uptime3 = re.compile(r"up (?P<d>\d+) days, (?P<h>\d+):(?P<m>\d+), \d+ user")

    def execute_cli(self):
        secs = mins = hours = days = 0
        c = self.cli("uptime")
        match = self.rx_uptime1.search(c)
        if match:
            secs = int(match.group("s"))
        else:
            match = self.rx_uptime2.search(c)
            if match:
                mins = int(match.group("m"))
            else:
                match = self.rx_uptime3.search(c)
                if match:
                    days = int(match.group("d"))
                    hours = int(match.group("h"))
                    mins = int(match.group("m"))
        return days * 86400 + hours * 3600 + mins * 60 + secs
