# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Hikvision.DS2CD.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import json
# NOC modules
from noc.core.http.client import fetch_sync
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Generic.Object.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        host = self.credentials.get("address", "")
        with self.profile.http(self) as data:
            url = "%s/api/integration/v1/fullobjinfo?oid=%s" % (host, data["id"])
            code, headers, body = fetch_sync(
                url,
                headers=data["coockies"],
                follow_redirects=True,
                allow_proxy=False
            )
            if code != 200:
                raise IOError("Invalid HTTP response: %s" % code)
            if json.loads(body)["result"] == "NoAuth":
                raise IOError("Not Authorized")
            print body
            res = json.loads(body)
            vendor = "None"
            platform = "None"
            version = "None"
            for r in res["properties"]:
                if r["name"] == u"Марка ТС":
                    vendor = r["val"]
                if r["name"] == u"Модель ТС":
                    platform = r["val"]
                if r["name"] == u"VIN-код":
                    version = r["val"]
            return {
                    "vendor": vendor,
                    "platform": platform,
                    "version": version
                }
