# ---------------------------------------------------------------------
# Eltex.LTP16N.get_cpe_status
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpestatus import IGetCPEStatus


class Script(BaseScript):
    name = "Eltex.LTP16N.get_cpe_status"
    interface = IGetCPEStatus

    def execute_cli(self, **kwargs):
        r = []
        for x in self.scripts.get_cpe():
            r.append(
                {
                    "interface": x["interface"],
                    "oper_status": x["status"] == "active",
                    "local_id": x["id"],
                    "global_id": x["global_id"],
                }
            )
        return r

    def execute_snmp(self, **kwargs):
        r = []
        for x in self.scripts.get_cpe():
            r.append(
                {
                    "interface": x["interface"],
                    "oper_status": x["status"] == "active",
                    "local_id": x["id"],
                    "global_id": x["global_id"],
                }
            )
        return r
