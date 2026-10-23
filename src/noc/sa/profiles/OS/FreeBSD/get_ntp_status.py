# ---------------------------------------------------------------------
# OS.FreeBSD.get_ntp_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetntpstatus import IGetNTPStatus


class Script(BaseScript):
    name = "OS.FreeBSD.get_ntp_status"
    cache = True
    interface = IGetNTPStatus
    rx_line = re.compile(
        r"^(?P<status>[\+\*\- ])(?P<address>\d+\.\d+\.\d+\.\d+)\s+"
        r"(?P<ref_id>\S+)\s+(?P<stratum>\d+)",
        re.MULTILINE,
    )
    status_map = client_map = {" ": "unknown", "-": "sane", "+": "selected", "*": "master"}

    def execute(self):
        s = self.cli("ntpq --command=peers -n")
        return [
            {
                "address": match.group("address"),
                "ref_id": match.group("ref_id"),
                "stratum": match.group("stratum"),
                "is_synchronized": match.group("status") == "*",
                "status": self.status_map[match.group("status")],
            }
            for match in self.rx_line.finditer(s)
        ]
