# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DAS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "DLink.DAS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("get system info")
        res = dict([(l.split(":", 1)[0].strip(),
                     l.split(":", 1)[1].strip() if len(l.split(":", 1)) > 1 else "")
                    for l in v.splitlines()])

        r = {
            "vendor": "DLink",
            "platform": res["Description"],
            "version": res["CPSwVersion"],
            "attributes": {
                "Boot PROM": res["DPSwVersion"],
                "HW version": res["DPSwVersion"],
            }
        }

        return r
