# ---------------------------------------------------------------------
# Beward.BD.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Beward.BD.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        res = self.http.get(
            "/cgi-bin/admin/param.cgi?action=list", json=False, cached=True, use_basic=True
        )
        r = {}
        for x in res.splitlines():
            if not x:
                continue
            try:
                k, v = x.split("=")
            except ValueError:
                continue
            r[k] = v
        return {
            "vendor": "Beward",
            "platform": r["root.Brand.ProdNbr"],
            "version": r["root.Properties.Firmware.Version"],
            "attributes": {
                # "Boot PROM": match.group("bootprom"),
                "Build Date": r["root.Properties.Firmware.BuildDate"],
                # "HW version": system_info["hardwareVersion"],
                # "Serial Number": system_info["serialNumber"]
                # "Firmware Type":
            },
        }
