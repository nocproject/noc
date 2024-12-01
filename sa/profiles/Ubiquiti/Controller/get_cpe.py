# ---------------------------------------------------------------------
# Ubiquiti.Controller.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import orjson

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE


class Script(BaseScript):
    """
    Clients: /v2/api/site/default/clients/history?onlyNonBlocked=true&includeUnifiDevices=true&withinHours=0
    """

    name = "Ubiquiti.Controller.get_cpe"
    interface = IGetCPE

    status_map = {
        1: "active",  # associated
        2: "inactive",  # disassociating
        3: "provisioning",  # downloading
    }

    def get_sites(self):
        v = self.http.post(
            "/v2/api/sites/overview/",
            orjson.dumps({}),
            headers={"Content-Type": b"application/json"},
            json=True,
            cached=True,
        )
        if not v["data"]:
            return ["default"]
        return [x["name"] for x in v["data"]]

    def execute(self, **kwargs):
        r = []
        sites = self.get_sites()
        for s in sites:
            v = self.http.get(f"/v2/api/site/{s}/device?separateUnmanaged=true", json=True)
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
                        "site": s,
                        # "location": ap_location,
                    }
                )
        return r
