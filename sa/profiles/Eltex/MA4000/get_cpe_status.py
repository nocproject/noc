# ---------------------------------------------------------------------
# Huawei.MA5600T.get_cpe_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpestatus import IGetCPEStatus


class Script(BaseScript):
    name = "Huawei.MA5600T.get_cpe_status"
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
