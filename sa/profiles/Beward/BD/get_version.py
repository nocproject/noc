# -*- coding: utf-8 -*-
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

    @property
    def execute(self):
        res = self.http.get("/cgi-bin/admin/param.cgi?action=list", json=False, cached=True, use_basic=True)
        r = {}
        for x in res.splitlines():
            if not x:
                continue
            k, v = x.split("=")
            r[k] = v

        ver = {
            "vendor": "Beward",
            "platform": r["root.Brand.ProdNbr"],
            "version": r["root.Properties.Firmware.Version"],
            "attributes":
                {"build": r["root.Properties.Firmware.BuildDate"]}
        }

        return ver
