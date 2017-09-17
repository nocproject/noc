# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RTBSv1.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from tornado.iostream import StreamClosedError


class Script(BaseScript):
    name = "Rotek.RTBSv1.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False

    def execute(self):
        try:
            c = self.cli("show software version")
        except self.CLISyntaxError:
            c = self.cli("show software-version")
        line = c.split(":")
        res = line[1].strip().split(".", 2)
        hwversion = "%s.%s" % (res[0], res[1])
        sres = res[2].split(".")
        sw = "%s.%s" % (sres[0], sres[1])
        result = {
            "vendor": "Rotek",
            "version": sw,
            "attributes": {
                "HW version": hwversion}
        }
        with self.profile.shell(self):
                v = self.cli("cat /etc/product", cached=True)
                for line in v.splitlines():
                    l = line.split(":", 1)
                    if "productName" in l[0]:
                        platform = l[1].strip().replace(" ",".").replace("\"","").replace(",","")
                        result["platform"] = platform
        return result
