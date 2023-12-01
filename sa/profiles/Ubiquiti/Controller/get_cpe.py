# ---------------------------------------------------------------------
# Ubiquiti.Controller.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE


class Script(BaseScript):
    name = "Ubiquiti.Controller.get_cpe"
    interface = IGetCPE

    status_map = {
        1: "active",  # associated
        2: "inactive",  # disassociating
        3: "provisioning",  # downloading
    }

    def execute(self, **kwargs):
        r = []
        v = self.http.get("/v2/api/site/default/device?separateUnmanaged=true", json=True)
        for d in v["network_devices"]:
            if d["device_type"] != "MANAGED" or not d["is_access_point"]:
                continue
            r.append(
                {
                    "vendor": "Ubiquiti",
                    "model": d["model"],
                    "version": d["version"],
                    "mac": d["mac"],
                    "status": "active" if d["state"] else "inactive",
                    "id": d["_id"],  # Use int command show ap inventory NAME
                    "global_id": d["mac"],
                    "type": "ap",
                    "name": d["name"],
                    "ip": d["ip"],
                    # "serial": ap_serial,
                    "description": "",
                    # "location": ap_location,
                }
            )
        return r
