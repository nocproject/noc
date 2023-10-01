# ---------------------------------------------------------------------
# Polus.Horizon.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from xml.etree import ElementTree

# NOC modules
from demjson3 import json_int
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Polus.Horizon.get_version"
    interface = IGetVersion
    cache = True

    rx_table = re.compile(r"(?P<pname>\S+)\s*\|(?P<punits>\S*)\s*\|(?P<pvalue>.+)\s*")

    def parse_output(self, result):
        r = {x["name"]: x["value"] for x in result}
        return r

    def execute_http(self, **kwargs):
        # v = self.http.get("/api/crates", json=True)
        # "isEmergencyMode"
        # v = self.http.get("/api/crates/params?names=SrNumber,sysName", json=True)
        # sn = v["params"][0]["value"]
        v = self.http.get(
            "/api/devices/params?crateId=1&slotNumber=25&names=pId,SwNumber,SrNumber,HwNumber",
            json=True,
        )
        r = self.parse_output(v["params"])
        return {
            "vendor": "Polus",
            "platform": r["pId"],
            "version": r["SwNumber"],
            "attributes": {"Serial Number": r["SrNumber"], "HW version": r["HwNumber"]},
        }

    def execute(self):
        if self.credentials.get("http_protocol") == "https":
            return self.execute_http()
        v = self.cli("show params cu")
        r = {}
        for match in self.rx_table.finditer(v):
            r[match.group("pname")] = match.group("pvalue").strip()
        return {
            "vendor": "Polus",
            "platform": r["pId"],
            "version": r["SwNumber"],
            "attributes": {
                "Serial Number": r["SrNumber"],
                "HW version": r["HwNumber"],
            },
        }
