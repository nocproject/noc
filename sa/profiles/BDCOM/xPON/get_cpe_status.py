# ---------------------------------------------------------------------
# BDCOM.xPON.get_cpe_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpestatus import IGetCPEStatus


class Script(BaseScript):
    name = "BDCOM.xPON.get_cpe_status"
    interface = IGetCPEStatus

    cache = True
    splitter = re.compile(r"\s*-+\n")

    status_map = {
        "auto-configured": True,
        "auto-configuring": True,
        "authenticated": True,
        "lost": False,
        "deregistered": False,
    }

    def execute_cli(self, **kwargs):
        r = []
        v = self.cli("show epon onu-information")
        for table in v.split("\n\n"):
            parts = self.splitter.split(table)
            for p in parts[1:]:
                for onu in p.split("\n"):
                    line = onu.split()
                    if len(line) >= 8:
                        r.append(
                            {
                                "oper_status": self.status_map[line[6]],
                                "local_id": line[0],  # Use int command show ap inventory NAME
                                "global_id": line[3],
                            }
                        )
                    else:
                        # Sometimes first fields overlaps
                        # IntfName   VendorID  ModelID    MAC Address    Description                     BindType  Status          Dereg Reason
                        # ---------- --------- ---------- -------------- ------------------------------- --------- --------------- -----------------
                        # EPON0/13:9 VSOL      D401       006d.61d4.6bf8 N/A                             static    auto-configured N/A
                        # EPON0/13:10xPON      101Z       e0e8.e61f.0759 N/A                             static    auto-configured N/A
                        r.append(
                            {
                                "oper_status": self.status_map[line[5]],
                                "local_id": line[0][0:11],
                                "global_id": line[2],
                            }
                        )
        return r
