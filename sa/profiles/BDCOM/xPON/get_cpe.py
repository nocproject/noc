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
from noc.sa.interfaces.igetcpe import IGetCPE


class Script(BaseScript):
    name = "BDCOM.xPON.get_cpe"
    interface = IGetCPE

    cache = True

    splitter = re.compile(r"\s*-+\n")

    status_map = {
        "auto-configured": "active",
        "auto-configuring": "active",
        "authenticated": "active",
        "lost": "inactive",
        "deregistered": "inactive",
    }

    #    detail_map = {
    #        "ont distance(m)": "ont_distance",
    #        "ont ip 0 address/mask": "ont_address",
    #        "last down cause": "down_cause",
    #    }

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
                            "vendor": line[1],
                            "model": line[2],
                            #                            "version": ap_sw_ver,
                            "mac": line[3],
                            "status": self.status_map[line[6]],
                            "id": line[0],  # Use int command show ap inventory NAME
                            "global_id": line[3],
                            "type": "ont",
                            #                            "name": line[0],
                            #                            "ip": ip_address,
                            "serial": line[3],
                            "description": "",
                        }
                    )
        return r
