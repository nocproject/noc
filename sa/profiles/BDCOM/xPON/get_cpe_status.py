# ---------------------------------------------------------------------
# BDCOM.xPON.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpestatus import IGetCPEStatus


class Script(BaseScript):
    name = "BDCOM.xPON.get_cpe"
    interface = IGetCPEStatus

    cache = True
    splitter = re.compile(r"\s*-+\n")

    status_map = {
        "auto-configured": "active",
        "auto-configuring": "active",
        "authenticated": "active",
        "lost": "inactive",
        "deregistered": "inactive",
    }

    def execute_cli(self, **kwargs):
        r = []
        v = self.cli("show epon onu-information")
        for table in v.split("\n\n"):
            parts = self.splitter.split(table)
            for p in parts[1:]:
                for onu in p.split("\n"):
                    line = onu.split()
                    r.append(
                        {
                            "oper_status": self.status_map[line[6]],
                            "local_id": line[0],  # Use int command show ap inventory NAME
                            "global_id": line[3],
                        }
                    )
        return r
