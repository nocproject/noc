# ---------------------------------------------------------------------
# Juniper.JUNOS.get_license
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_ntp_status import Script as BaseScript
from noc.sa.interfaces.igetntpstatus import IGetNTPStatus


class Script(BaseScript):
    name = "Juniper.JUNOS.get_ntp_status"
    interface = IGetNTPStatus

    rx_line = re.compile(
        r"^(?P<status> |x|\.|-|\+|#|\*|o)(?P<address>\S+)\s+(?P<refid>\S+)\s+\S+\s+(?P<stratum>\d+)\s+(?P<peer_type>\S+)(\s+\S+){6}$",
        re.MULTILINE,
    )

    def execute_cli(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show ntp associations")):
            assoc_status = match.group("status")
            assoc_address = match.group("address")
            assoc_refid = match.group("refid")
            assoc_stratum = match.group("stratum")

            assoc = {
                "name": assoc_address,
                "address": assoc_address,
                "stratum": assoc_stratum,
                "ref_id": assoc_refid,
            }

            if assoc_status in (" ", "x", ".", "-"):
                assoc["status"] = "unknown"
                assoc["is_synchronized"] = False
            elif assoc_status == "+":
                assoc["status"] = "selected"
                assoc["is_synchronized"] = False
            elif assoc_status in ("#", "*", "o"):
                assoc["status"] = "master"
                assoc["is_synchronized"] = True

            r.append(assoc)
        return r
