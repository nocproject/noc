# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from .profile import PolusParam


class Script(BaseScript):
    name = "IRE-Polus.Horizon.get_version"
    interface = IGetVersion
    cache = True

    rx_table = re.compile(r"(?P<pname>\S+)\s*\|(?P<punits>\S*)\s*\|(?P<pvalue>.+)\s*")

    def execute_http(self, **kwargs):
        # v = self.http.get("/api/crates", json=True)
        # "isEmergencyMode"
        # v = self.http.get("/api/crates/params?names=SrNumber,sysName", json=True)
        #
        # sn = v["params"][0]["value"]
        c = self.http.get("/api/crates", json=True, cached=True)
        platform = c["crates"][0]["chassis"]
        crate, cu_slot = self.profile.get_cu_slot(self)
        v = self.http.get(
            f"/api/devices/params?crateId={crate}&slotNumber={cu_slot}"
            f"&names=pId,SwNumber,SrNumber,HwNumber&fields=name,value,description",
            json=True,
        )
        r = {}
        for p in v["params"]:
            p = PolusParam.from_code(**p)
            r[p.name] = p
        return {
            "vendor": "IRE-Polus",
            "platform": platform,
            "version": r["SwNumber"].value,
            "attributes": {"Serial Number": r["SrNumber"].value, "HW version": r["HwNumber"].value},
        }

    def execute_cli(self):
        if self.credentials.get("http_protocol") == "https":
            return self.execute_http()
        v = self.cli("show params cu")
        r = {}
        for match in self.rx_table.finditer(v):
            r[match.group("pname")] = match.group("pvalue").strip()
        return {
            "vendor": "IRE-Polus",
            "platform": r["pId"],
            "version": r["SwNumber"],
            "attributes": {
                "Serial Number": r["SrNumber"],
                "HW version": r["HwNumber"],
            },
        }
